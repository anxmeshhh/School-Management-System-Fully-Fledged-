/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NOTIFICATION CLIENT — School Management System
 * Handles: Polling, Badge, Dropdown, Toasts, Sound, Vibration, Grouping
 * ═══════════════════════════════════════════════════════════════════════════
 */

(function () {
    'use strict';

    // ─── Config ────────────────────────────────────────────────────────────
    const POLL_INTERVAL = 30000;     // Poll every 30 seconds
    const TOAST_DURATION = 5000;     // Toast visible for 5 seconds
    const MAX_TOASTS = 3;           // Max simultaneous toasts

    // ─── Category Icons Map ────────────────────────────────────────────────
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
    let lastUnreadCount = 0;
    let isPolling = false;
    let pollTimer = null;
    let notifAudioCtx = null;
    let isPanelOpen = false;

    // ─── Initialize ────────────────────────────────────────────────────────
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
    }

    const VAPID_PUBLIC_KEY = "BLNqmzATvl4GJpv1khAm8Uz1FoXC13H7-gEuD4XtY5JpqQIoGfL4g7_Gm5Mc2kejNgy67LTyWQRLozHhoWgQ7fI";

    function urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i);
        return outputArray;
    }

    // ─── System Notification Permissions & Popups ──────────────────────────
    function setupPermissionTriggers() {
        const requestPermissionOnce = () => {
            if ("Notification" in window && Notification.permission === 'default') {
                Notification.requestPermission().then(permission => {
                    console.log('[Notif] System notification permission:', permission);
                    if (permission === 'granted') {
                        subscribeToPush();
                    }
                });
            } else if ("Notification" in window && Notification.permission === 'granted') {
                subscribeToPush();
            }
            
            // Preload audio on first click to satisfy browser auto-play policies
            if (!window.notifAudioEl) {
                window.notifAudioEl = new Audio('/static/users/audio/notification.wav');
                window.notifAudioEl.volume = 0.8;
                window.notifAudioEl.load();
            }
            document.removeEventListener('click', requestPermissionOnce);
            document.removeEventListener('touchstart', requestPermissionOnce);
        };
        document.addEventListener('click', requestPermissionOnce);
        document.addEventListener('touchstart', requestPermissionOnce);
    }

    function subscribeToPush() {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            navigator.serviceWorker.register('/sw.js').then(function(swReg) {
                swReg.pushManager.getSubscription().then(function(subscription) {
                    if (subscription) {
                        sendSubscriptionToServer(subscription);
                    } else {
                        swReg.pushManager.subscribe({
                            userVisibleOnly: true,
                            applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
                        }).then(function(newSubscription) {
                            sendSubscriptionToServer(newSubscription);
                        }).catch(function(err) {
                            console.log('[Notif] Failed to subscribe to web push: ', err);
                        });
                    }
                });
            }).catch(function(error) {
                console.error('[Notif] Service Worker Error', error);
            });
        }
    }

    function sendSubscriptionToServer(subscription) {
        fetch('/api/notifications/subscribe/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                type: userType,
                id: userId,
                subscription: subscription
            })
        }).catch(err => console.log('[Notif] Subscription sync error:', err));
    }

    function requestSystemNotificationPermission() {
        if (!("Notification" in window)) return;
        if (Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') subscribeToPush();
            });
        } else if (Notification.permission === 'granted') {
            subscribeToPush();
        }
    }

    function triggerSystemNotification(title, message, actionUrl) {
        if (!("Notification" in window) || Notification.permission !== "granted") return;

        const options = {
            body: message,
            icon: '/static/users/images/adminlogo.jpg',
            badge: '/static/users/images/adminlogo.jpg',
            vibrate: [100, 50, 100],
            requireInteraction: false
        };

        try {
            const notification = new Notification(title, options);
            if (actionUrl) {
                notification.onclick = function (event) {
                    event.preventDefault();
                    window.focus();
                    window.location.href = actionUrl;
                    notification.close();
                };
            }
        } catch (e) {
            console.warn('[Notif] Error creating system notification:', e.message);
        }
    }

    function fetchAndTriggerSystemNotifications(count) {
        fetch(`/api/notifications/?type=${userType}&id=${userId}`)
            .then(r => r.json())
            .then(data => {
                const notifications = data.notifications || [];
                // Get the newest unread notifications up to count
                const unreadNotifs = notifications.filter(n => !n.is_read).slice(0, count);
                unreadNotifs.forEach(n => {
                    const icon = CATEGORY_ICONS[n.category] || '🔔';
                    triggerSystemNotification(`${icon} ${n.title}`, n.message, n.action_url);
                });
            })
            .catch(err => console.warn('[Notif] Error fetching for system notification:', err));
    }

    // ─── UI Setup ──────────────────────────────────────────────────────────
    function setupUI() {
        const bell = document.getElementById('notificationBell');
        const panel = document.getElementById('notificationPanel');

        if (!bell || !panel) return;

        // Wrap bell in a container for badge positioning
        const wrapper = document.createElement('span');
        wrapper.className = 'bell-wrapper';
        bell.parentNode.insertBefore(wrapper, bell);
        wrapper.appendChild(bell);

        // Create badge
        const badge = document.createElement('span');
        badge.id = 'notifBadge';
        badge.className = 'notification-badge';
        badge.textContent = '0';
        wrapper.appendChild(badge);

        // Replace static panel content with dynamic structure
        panel.innerHTML = `
            <div class="notif-panel-header">
                <h3>Notifications</h3>
                <button class="notif-mark-all-btn" id="notifMarkAllBtn">Mark all read</button>
            </div>
            <div class="notif-panel-body" id="notifPanelBody">
                ${getLoadingHTML()}
            </div>
        `;

        // Restyle panel class
        panel.classList.remove('notification-panel');
        panel.classList.add('notif-panel');

        // Bell click
        bell.addEventListener('click', (e) => {
            e.stopPropagation();
            requestSystemNotificationPermission();
            isPanelOpen = !isPanelOpen;
            panel.classList.toggle('active', isPanelOpen);
            if (isPanelOpen) {
                fetchNotifications();
            }
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target) && !panel.contains(e.target)) {
                panel.classList.remove('active');
                isPanelOpen = false;
            }
        });

        // Mark all read button
        document.getElementById('notifMarkAllBtn').addEventListener('click', (e) => {
            e.stopPropagation();
            markAllRead();
        });
    }

    function setupToastContainer() {
        if (document.getElementById('notifToastContainer')) return;
        const container = document.createElement('div');
        container.id = 'notifToastContainer';
        container.className = 'notif-toast-container';
        document.body.appendChild(container);
    }

    // ─── Polling ───────────────────────────────────────────────────────────
    function startPolling() {
        if (isPolling) return;
        isPolling = true;
        pollTimer = setInterval(fetchUnreadCount, POLL_INTERVAL);
    }

    function stopPolling() {
        isPolling = false;
        if (pollTimer) clearInterval(pollTimer);
    }

    // ─── API Calls ─────────────────────────────────────────────────────────
    function fetchUnreadCount() {
        fetch(`/api/notifications/count/?type=${userType}&id=${userId}`)
            .then(r => r.json())
            .then(data => {
                const newCount = data.count || 0;
                updateBadge(newCount);

                // If count increased, trigger alerts
                if (newCount > lastUnreadCount && lastUnreadCount >= 0) {
                    const diff = newCount - lastUnreadCount;
                    if (lastUnreadCount > 0) {
                        // New notifications arrived
                        playNotificationSound();
                        triggerVibration();
                        
                        const hasSystemNotif = ("Notification" in window && Notification.permission === "granted");
                        
                        if (!isPanelOpen && !hasSystemNotif) {
                            showNewNotifToast(diff);
                        }
                        
                        // Trigger native system notification
                        if (hasSystemNotif) {
                            fetchAndTriggerSystemNotifications(diff);
                        }
                    }
                }
                lastUnreadCount = newCount;
            })
            .catch(err => console.warn('[Notif] Count fetch error:', err));
    }

    function fetchNotifications() {
        const body = document.getElementById('notifPanelBody');
        if (!body) return;
        body.innerHTML = getLoadingHTML();

        fetch(`/api/notifications/?type=${userType}&id=${userId}`)
            .then(r => r.json())
            .then(data => {
                const notifications = data.notifications || [];
                renderNotifications(notifications);
            })
            .catch(err => {
                console.warn('[Notif] Fetch error:', err);
                body.innerHTML = getEmptyHTML('Error loading notifications');
            });
    }

    function markAsRead(notifId, groupIds) {
        if (groupIds && groupIds.length > 1) {
            // Mark group as read - send all IDs
            fetch(`/api/notifications/read/${notifId}/?type=${userType}&id=${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ group_ids: groupIds }),
            }).then(() => {
                fetchUnreadCount();
                if (isPanelOpen) fetchNotifications();
            });
        } else {
            fetch(`/api/notifications/read/${notifId}/?type=${userType}&id=${userId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
            }).then(() => {
                fetchUnreadCount();
                if (isPanelOpen) fetchNotifications();
            });
        }
    }

    function markAllRead() {
        fetch(`/api/notifications/read-all/?type=${userType}&id=${userId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
        }).then(() => {
            fetchUnreadCount();
            if (isPanelOpen) fetchNotifications();
        });
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
                     data-url="${n.action_url || ''}"
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

    function updateBadge(count) {
        const badge = document.getElementById('notifBadge');
        if (!badge) return;

        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.classList.add('visible');

            // Pulse animation
            if (count > lastUnreadCount && lastUnreadCount > 0) {
                badge.classList.remove('pulse-badge');
                void badge.offsetWidth; // Force reflow
                badge.classList.add('pulse-badge');

                // Ring the bell
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

    // ─── Toast Notifications ───────────────────────────────────────────────
    function showNewNotifToast(count) {
        const container = document.getElementById('notifToastContainer');
        if (!container) return;

        // Limit toasts
        const existing = container.querySelectorAll('.notif-toast');
        if (existing.length >= MAX_TOASTS) {
            existing[0].remove();
        }

        const toast = document.createElement('div');
        toast.className = 'notif-toast';
        toast.innerHTML = `
            <span class="notif-toast-icon">🔔</span>
            <div class="notif-toast-body">
                <div class="notif-toast-title">${count === 1 ? 'New notification' : count + ' new notifications'}</div>
                <div class="notif-toast-message">Click to view</div>
            </div>
            <button class="notif-toast-close" onclick="event.stopPropagation(); this.parentElement.classList.add('hiding'); setTimeout(() => this.parentElement.remove(), 400);">✕</button>
        `;

        toast.addEventListener('click', () => {
            const bell = document.getElementById('notificationBell');
            if (bell) bell.click();
            toast.classList.add('hiding');
            setTimeout(() => toast.remove(), 400);
        });

        container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                toast.classList.add('show');
            });
        });

        // Auto-dismiss
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
            const playPromise = window.notifAudioEl.play();
            if (playPromise !== undefined) {
                playPromise.catch(error => {
                    console.log('[Notif] Audio blocked by browser policy:', error);
                });
            }
        } catch (e) {
            console.log('[Notif] Sound error:', e.message);
        }
    }

    function triggerVibration() {
        try {
            if (navigator.vibrate) {
                navigator.vibrate([100, 50, 100]); // Short double vibration
            }
        } catch (e) {
            // Vibration not supported
        }
    }

    // ─── Helpers ───────────────────────────────────────────────────────────
    function relativeTime(isoStr) {
        if (!isoStr) return '';
        const date = new Date(isoStr);
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHr = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHr / 24);

        if (diffSec < 60) return 'Just now';
        if (diffMin < 60) return diffMin + (diffMin === 1 ? ' min ago' : ' mins ago');
        if (diffHr < 24) return diffHr + (diffHr === 1 ? ' hour ago' : ' hours ago');
        if (diffDay < 7) return diffDay + (diffDay === 1 ? ' day ago' : ' days ago');
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    function escapeHTML(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function getCSRFToken() {
        const cookie = document.cookie.split(';')
            .find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    function getLoadingHTML() {
        let html = '<div class="notif-loading">';
        for (let i = 0; i < 3; i++) {
            html += `
                <div class="notif-skeleton">
                    <div class="notif-skeleton-icon"></div>
                    <div class="notif-skeleton-content">
                        <div class="notif-skeleton-line"></div>
                        <div class="notif-skeleton-line short"></div>
                        <div class="notif-skeleton-line tiny"></div>
                    </div>
                </div>
            `;
        }
        html += '</div>';
        return html;
    }

    function getEmptyHTML(text) {
        return `
            <div class="notif-empty">
                <div class="notif-empty-icon">🎉</div>
                <div class="notif-empty-text">${text || 'No notifications yet'}</div>
                <div class="notif-empty-sub">You're all caught up!</div>
            </div>
        `;
    }

    // ─── Public: Click Handler ─────────────────────────────────────────────
    function handleClick(el) {
        const notifId = el.dataset.id;
        const url = el.dataset.url;
        let groupIds = [];
        try {
            groupIds = JSON.parse(el.dataset.groupIds || '[]');
        } catch (e) { /* ignore */ }

        // Mark as read
        if (el.classList.contains('unread')) {
            markAsRead(notifId, groupIds);
        }

        // Navigate if URL provided
        if (url) {
            window.location.href = url;
        }
    }

    // ─── Expose Public API ─────────────────────────────────────────────────
    window.NotifClient = {
        handleClick: handleClick,
        refresh: fetchUnreadCount,
    };

    // ─── Boot ──────────────────────────────────────────────────────────────
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
