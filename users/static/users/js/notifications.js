/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NOTIFICATION CLIENT — School Management System
 * Handles: Polling, Badge, Dropdown, Toasts, Sound, Vibration, Grouping
 * ═══════════════════════════════════════════════════════════════════════════
 */

(function () {
    'use strict';

    // ─── Config ────────────────────────────────────────────────────────────
    const POLL_INTERVAL = 30000;
    const POLL_MAX = 300000; // 5 min cap for backoff
    const TOAST_DURATION = 5000;
    const MAX_TOASTS = 3;
    const MAX_SEEN_IDS = 500;

    // ─── Category Icons ────────────────────────────────────────────────────
    const CATEGORY_ICONS = {
        leave: '📝',
        attendance: '✅',
        circular: '📢',
        homework: '📝',
        marks: '📊',
        timetable: '📅',
        exam: '📋',
        fee: '💰',
        study_material: '📚',
        profile: '👤',
        auth: '🔐',
        student: '🎓',
        class: '🏫',
        user: '👥',
    };

    // ─── State ─────────────────────────────────────────────────────────────
    let userType = null;
    let userId = null;
    let lastUnreadCount = -1;
    let isPolling = false;
    let pollTimer = null;
    let currentInterval = POLL_INTERVAL;
    let errorStreak = 0;
    let isPanelOpen = false;
    let lastNotifIds = new Set();
    let uiInitialised = false;

    // Stored so destroy() can remove them
    const _listeners = [];

    const VAPID_PUBLIC_KEY = "BLNqmzATvl4GJpv1khAm8Uz1FoXC13H7-gEuD4XtY5JpqQIoGfL4g7_Gm5Mc2kejNgy67LTyWQRLozHhoWgQ7fI";

    // ─── Init ──────────────────────────────────────────────────────────────
    function init() {
        const body = document.body;
        userType = body.dataset.userType || null;
        userId = body.dataset.userId || null;

        if (!userType || !userId) {
            console.log('[Notif] No user context, notifications disabled.');
            return;
        }

        setupUI();
        setupToastContainer();
        fetchUnreadCount();
        startPolling();
        setupPermissionTriggers();

        const onVisibility = () => {
            if (!document.hidden) fetchUnreadCount();
        };
        document.addEventListener('visibilitychange', onVisibility);
        _listeners.push({ el: document, type: 'visibilitychange', fn: onVisibility });
    }

    // ─── VAPID Helper ──────────────────────────────────────────────────────
    function urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const output = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) output[i] = rawData.charCodeAt(i);
        return output;
    }

    // ─── Permissions & Push ────────────────────────────────────────────────
    function setupPermissionTriggers() {
        const requestOnce = () => {
            if (!window.notifAudioEl) {
                window.notifAudioEl = new Audio('/static/users/audio/notification.wav');
                window.notifAudioEl.volume = 0.8;
                window.notifAudioEl.load();
            }

            if (!("Notification" in window)) return;

            if (Notification.permission === 'default') {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') subscribeToPush();
                });
            } else if (Notification.permission === 'granted') {
                subscribeToPush();
            }

            document.removeEventListener('click', requestOnce);
            document.removeEventListener('touchstart', requestOnce);
        };
        document.addEventListener('click', requestOnce);
        document.addEventListener('touchstart', requestOnce);
    }

    function subscribeToPush() {
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) return;

        navigator.serviceWorker.ready.then(swReg => {
            swReg.pushManager.getSubscription().then(subscription => {
                if (subscription) {
                    const key = 'push_synced_' + userId;
                    if (!sessionStorage.getItem(key)) {
                        sendSubscriptionToServer(subscription);
                        sessionStorage.setItem(key, '1');
                    }
                } else {
                    swReg.pushManager.subscribe({
                        userVisibleOnly: true,
                        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
                    }).then(newSub => {
                        sendSubscriptionToServer(newSub);
                        sessionStorage.setItem('push_synced_' + userId, '1');
                    }).catch(err => console.warn('[Notif] Push subscribe failed:', err));
                }
            });
        }).catch(err => console.warn('[Notif] SW not ready:', err));
    }

    function sendSubscriptionToServer(subscription) {
        fetch('/api/notifications/subscribe/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ type: userType, id: userId, subscription })
        }).catch(err => console.warn('[Notif] Subscription sync error:', err));
    }

    function triggerSystemNotification(title, message, actionUrl) {
        if (!("Notification" in window) || Notification.permission !== 'granted') return;
        try {
            const n = new Notification(title, {
                body: message,
                icon: '/static/users/images/adminlogo.jpg',
                badge: '/static/users/images/adminlogo.jpg',
                vibrate: [100, 50, 100],
                requireInteraction: false
            });
            if (actionUrl) {
                n.onclick = e => {
                    e.preventDefault();
                    window.focus();
                    window.location.href = actionUrl;
                    n.close();
                };
            }
        } catch (e) {
            console.warn('[Notif] System notification error:', e.message);
        }
    }

    // ─── UI Setup ──────────────────────────────────────────────────────────
    function setupUI() {
        if (uiInitialised) return;
        uiInitialised = true;

        const bell = document.getElementById('notificationBell');
        const panel = document.getElementById('notificationPanel');
        if (!bell || !panel) return;

        const wrapper = document.createElement('span');
        wrapper.className = 'bell-wrapper';
        bell.parentNode.insertBefore(wrapper, bell);
        wrapper.appendChild(bell);

        const badge = document.createElement('span');
        badge.id = 'notifBadge';
        badge.className = 'notification-badge';
        badge.textContent = '0';
        wrapper.appendChild(badge);

        panel.innerHTML = `
            <div class="notif-panel-header">
                <h3>Notifications</h3>
                <button class="notif-mark-all-btn" id="notifMarkAllBtn">Mark all read</button>
            </div>
            <div class="notif-panel-body" id="notifPanelBody">
                ${getLoadingHTML()}
            </div>
        `;
        panel.classList.remove('notification-panel');
        panel.classList.add('notif-panel');

        const onBellClick = e => {
            e.stopPropagation();
            isPanelOpen = !isPanelOpen;
            panel.classList.toggle('active', isPanelOpen);
            if (isPanelOpen) fetchNotifications();
        };
        bell.addEventListener('click', onBellClick);
        _listeners.push({ el: bell, type: 'click', fn: onBellClick });

        const onDocClick = e => {
            if (!wrapper.contains(e.target) && !panel.contains(e.target)) {
                panel.classList.remove('active');
                isPanelOpen = false;
            }
        };
        document.addEventListener('click', onDocClick);
        _listeners.push({ el: document, type: 'click', fn: onDocClick });

        document.getElementById('notifMarkAllBtn').addEventListener('click', e => {
            e.stopPropagation();
            markAllRead();
        });
    }

    function setupToastContainer() {
        if (document.getElementById('notifToastContainer')) return;
        const c = document.createElement('div');
        c.id = 'notifToastContainer';
        c.className = 'notif-toast-container';
        document.body.appendChild(c);
    }

    // ─── Polling ───────────────────────────────────────────────────────────
    function startPolling() {
        if (isPolling) return;
        isPolling = true;
        scheduleNextPoll(currentInterval);
    }

    function scheduleNextPoll(delay) {
        clearTimeout(pollTimer);
        pollTimer = setTimeout(() => {
            fetchUnreadCount();
            scheduleNextPoll(currentInterval);
        }, delay);
    }

    function onFetchSuccess() {
        if (errorStreak > 0) {
            errorStreak = 0;
            currentInterval = POLL_INTERVAL;
            // Reset to normal interval immediately
            scheduleNextPoll(currentInterval);
        }
    }

    function onFetchError() {
        errorStreak++;
        currentInterval = Math.min(currentInterval * 2, POLL_MAX);
        scheduleNextPoll(currentInterval);
    }

    // ─── Core Fetch: Unread Count ──────────────────────────────────────────
    function fetchUnreadCount() {
        // Skip if tab is not visible
        if (document.hidden) return;

        fetch(`/api/notifications/count/?type=${userType}&id=${userId}`)
            .then(r => {
                if (!r.ok) throw new Error('count fetch failed');
                return r.json();
            })
            .then(data => {
                onFetchSuccess();
                const newCount = data.count || 0;

                // First poll: set baseline silently
                if (lastUnreadCount === -1) {
                    lastUnreadCount = newCount;
                    updateBadge(newCount);
                    return;
                }

                const prevCount = lastUnreadCount;
                lastUnreadCount = newCount;
                updateBadge(newCount, prevCount);

                if (newCount > prevCount) {
                    const diff = newCount - prevCount;
                    playNotificationSound();
                    triggerVibration();

                    const hasPermission = ("Notification" in window &&
                        Notification.permission === 'granted');

                    if (hasPermission) {
                        fetchNewNotificationsAndAlert(diff);
                    } else if (!isPanelOpen) {
                        showNewNotifToast(diff);
                    }
                }
            })
            .catch(err => {
                console.warn('[Notif] Count fetch error:', err);
                onFetchError();
            });
    }

    function fetchNewNotificationsAndAlert(count) {
        fetch(`/api/notifications/?type=${userType}&id=${userId}`)
            .then(r => r.json())
            .then(data => {
                const notifications = data.notifications || [];

                const newNotifs = notifications
                    .filter(n => !n.is_read && !lastNotifIds.has(String(n.id)))
                    .slice(0, count);

                addToSeenIds(notifications.map(n => String(n.id)));

                if (newNotifs.length === 0) {
                    if (!isPanelOpen) showNewNotifToast(count);
                    return;
                }

                newNotifs.forEach(n => {
                    const icon = CATEGORY_ICONS[n.category] || '🔔';
                    triggerSystemNotification(`${icon} ${n.title}`, n.message, n.action_url);
                });

                if (!isPanelOpen) showRichToast(newNotifs[0], newNotifs.length);
                if (isPanelOpen) fetchNotifications();
            })
            .catch(err => console.warn('[Notif] New notif fetch error:', err));
    }

    // ─── Fetch Full List ───────────────────────────────────────────────────
    function fetchNotifications() {
        const body = document.getElementById('notifPanelBody');
        if (!body) return;
        body.innerHTML = getLoadingHTML();

        fetch(`/api/notifications/?type=${userType}&id=${userId}`)
            .then(r => {
                if (!r.ok) throw new Error('notif fetch failed');
                return r.json();
            })
            .then(data => {
                const notifications = data.notifications || [];
                addToSeenIds(notifications.map(n => String(n.id)));
                renderNotifications(notifications);
            })
            .catch(err => {
                console.warn('[Notif] Fetch error:', err);
                const b = document.getElementById('notifPanelBody');
                if (b) b.innerHTML = getEmptyHTML('Error loading notifications');
            });
    }

    // ─── Seen IDs helper ──────────────────────────────────────────────────
    function addToSeenIds(ids) {
        ids.forEach(id => lastNotifIds.add(id));
        if (lastNotifIds.size > MAX_SEEN_IDS) {
            lastNotifIds = new Set([...lastNotifIds].slice(-MAX_SEEN_IDS));
        }
    }

    // ─── Mark Read ─────────────────────────────────────────────────────────
    function markAsRead(notifId, groupIds) {
        const hasGroup = groupIds && groupIds.length > 1;
        fetch(`/api/notifications/read/${notifId}/?type=${userType}&id=${userId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                ...(hasGroup && { 'Content-Type': 'application/json' })
            },
            body: hasGroup ? JSON.stringify({ group_ids: groupIds }) : undefined,
        })
            .then(r => {
                if (!r.ok) throw new Error('mark read failed');
                fetchUnreadCount();
                if (isPanelOpen) fetchNotifications();
            })
            .catch(err => console.warn('[Notif] Mark read error:', err));
    }

    function markAllRead() {
        fetch(`/api/notifications/read-all/?type=${userType}&id=${userId}`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() },
        })
            .then(r => {
                if (!r.ok) throw new Error('mark all read failed');
                const prev = lastUnreadCount;
                lastUnreadCount = 0;
                updateBadge(0, prev);
                if (isPanelOpen) fetchNotifications();
            })
            .catch(err => console.warn('[Notif] Mark all read error:', err));
    }

    // ─── Rendering ─────────────────────────────────────────────────────────
    function renderNotifications(notifications) {
        const body = document.getElementById('notifPanelBody');
        if (!body) return;

        if (!notifications.length) {
            body.innerHTML = getEmptyHTML();
            return;
        }

        let html = '';
        notifications.forEach(n => {
            const icon = CATEGORY_ICONS[n.category] || '🔔';
            const catClass = 'cat-' + (n.category || 'default');
            const readClass = n.is_read ? '' : 'unread';
            const time = relativeTime(n.created_at);
            const groupBadge = n.group_count > 1
                ? `<span class="notif-group-badge">${n.group_count}×</span>`
                : '';
            const groupIds = n.group_ids ? JSON.stringify(n.group_ids) : '[]';

            html += `
                <div class="notif-item ${readClass}"
                     data-id="${n.id}"
                     data-url="${escapeAttr(n.action_url || '')}"
                     data-group-ids='${groupIds}'
                     onclick="window.NotifClient.handleClick(this)">
                    <div class="notif-icon ${catClass}">${icon}</div>
                    <div class="notif-content">
                        <div class="notif-title">${escapeHTML(n.title)} ${groupBadge}</div>
                        <div class="notif-message">${escapeHTML(n.message)}</div>
                        <div class="notif-time">${time}</div>
                    </div>
                </div>
            `;
        });

        body.innerHTML = html;
    }

    function updateBadge(count, prevCount) {
        const badge = document.getElementById('notifBadge');
        if (!badge) return;

        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.classList.add('visible');

            if (prevCount !== undefined && count > prevCount) {
                badge.classList.remove('pulse-badge');
                void badge.offsetWidth;
                badge.classList.add('pulse-badge');

                const bell = document.getElementById('notificationBell');
                if (bell) {
                    bell.classList.remove('bell-ring');
                    void bell.offsetWidth;
                    bell.classList.add('bell-ring');
                }
            }
        } else {
            badge.classList.remove('visible');
        }
    }

    // ─── Toasts ────────────────────────────────────────────────────────────
    function showRichToast(notif, totalCount) {
        const icon = CATEGORY_ICONS[notif.category] || '🔔';
        const title = totalCount > 1 ? `${totalCount} new notifications` : `${icon} ${notif.title}`;
        const message = totalCount > 1 ? `Latest: ${notif.title}` : notif.message;
        _showToast(title, message);
    }

    function showNewNotifToast(count) {
        _showToast(
            count === 1 ? 'New notification' : `${count} new notifications`,
            'Click to view'
        );
    }

    function _showToast(title, message) {
        const container = document.getElementById('notifToastContainer');
        if (!container) return;

        const existing = container.querySelectorAll('.notif-toast');
        if (existing.length >= MAX_TOASTS) existing[0].remove();

        const toast = document.createElement('div');
        toast.className = 'notif-toast';
        toast.innerHTML = `
            <span class="notif-toast-icon">🔔</span>
            <div class="notif-toast-body">
                <div class="notif-toast-title">${escapeHTML(title)}</div>
                <div class="notif-toast-message">${escapeHTML(message)}</div>
            </div>
            <button class="notif-toast-close"
                onclick="event.stopPropagation();this.parentElement.classList.add('hiding');setTimeout(()=>this.parentElement.remove(),400)">✕</button>
        `;

        toast.addEventListener('click', () => {
            const bell = document.getElementById('notificationBell');
            if (bell) bell.click();
            toast.classList.add('hiding');
            setTimeout(() => toast.remove(), 400);
        });

        container.appendChild(toast);
        requestAnimationFrame(() => requestAnimationFrame(() => toast.classList.add('show')));

        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('hiding');
                setTimeout(() => toast.remove(), 400);
            }
        }, TOAST_DURATION);
    }

    // ─── Sound & Vibration ─────────────────────────────────────────────────
    function playNotificationSound() {
        try {
            if (!window.notifAudioEl) {
                window.notifAudioEl = new Audio('/static/users/audio/notification.wav');
                window.notifAudioEl.volume = 0.8;
            }
            window.notifAudioEl.currentTime = 0;
            const p = window.notifAudioEl.play();
            if (p) p.catch(() => { });
        } catch (e) {
            console.log('[Notif] Sound error:', e.message);
        }
    }

    function triggerVibration() {
        try { if (navigator.vibrate) navigator.vibrate([100, 50, 100]); } catch (e) { }
    }

    // ─── Helpers ───────────────────────────────────────────────────────────
    function relativeTime(isoStr) {
        if (!isoStr) return '';
        // Clamp to 0 — server clock drift can produce negative diff
        const diff = Math.max(0, Date.now() - new Date(isoStr).getTime());
        const sec = Math.floor(diff / 1000);
        const min = Math.floor(sec / 60);
        const hr = Math.floor(min / 60);
        const day = Math.floor(hr / 24);

        if (sec < 60) return 'Just now';
        if (min < 60) return min + (min === 1 ? ' min ago' : ' mins ago');
        if (hr < 24) return hr + (hr === 1 ? ' hour ago' : ' hours ago');
        if (day < 7) return day + (day === 1 ? ' day ago' : ' days ago');
        return new Date(isoStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    function escapeHTML(str) {
        if (!str) return '';
        const d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }

    function escapeAttr(str) {
        return str.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // Regex-based — safe against base64 = chars in the token value
    function getCSRFToken() {
        const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    function getLoadingHTML() {
        let h = '<div class="notif-loading">';
        for (let i = 0; i < 3; i++) {
            h += `<div class="notif-skeleton">
                    <div class="notif-skeleton-icon"></div>
                    <div class="notif-skeleton-content">
                        <div class="notif-skeleton-line"></div>
                        <div class="notif-skeleton-line short"></div>
                        <div class="notif-skeleton-line tiny"></div>
                    </div>
                  </div>`;
        }
        return h + '</div>';
    }

    function getEmptyHTML(text) {
        return `<div class="notif-empty">
                    <div class="notif-empty-icon">🎉</div>
                    <div class="notif-empty-text">${escapeHTML(text) || 'No notifications yet'}</div>
                    <div class="notif-empty-sub">You're all caught up!</div>
                </div>`;
    }

    // ─── Public API ────────────────────────────────────────────────────────
    function handleClick(el) {
        const notifId = el.dataset.id;
        const url = el.dataset.url;
        let groupIds = [];
        try { groupIds = JSON.parse(el.dataset.groupIds || '[]'); } catch (e) { }

        if (el.classList.contains('unread')) markAsRead(notifId, groupIds);
        if (url) window.location.href = url;
    }

    // Clears poll timer and all tracked listeners — call on SPA page teardown
    function destroy() {
        clearTimeout(pollTimer);
        isPolling = false;
        _listeners.forEach(({ el, type, fn }) => el.removeEventListener(type, fn));
        _listeners.length = 0;
    }

    window.NotifClient = {
        handleClick,
        refresh: fetchUnreadCount,
        destroy,
    };

    // ─── Boot ──────────────────────────────────────────────────────────────
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();