/**
 * Service Worker — School Management System
 * Handles: Push, Click, Close, Subscription Renewal, Offline Queue, Background Sync
 */

'use strict';

const SW_VERSION = 'v2';
const OFFLINE_QUEUE_KEY = 'offline_push_queue';
const MAX_QUEUE = 20;

// ─── Lifecycle ────────────────────────────────────────────────────────────────

self.addEventListener('install', function (event) {
    // Take over immediately — don't wait for old SW to die
    event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', function (event) {
    // Claim all open clients so this SW controls them right away
    event.waitUntil(self.clients.claim());
});


// ─── Push ─────────────────────────────────────────────────────────────────────

self.addEventListener('push', function (event) {
    event.waitUntil(handlePush(event));
});

async function handlePush(event) {
    let data;

    // Gracefully handle malformed or empty push payloads
    try {
        data = event.data ? event.data.json() : null;
    } catch (e) {
        console.error('[SW] Push payload parse error:', e);
        data = null;
    }

    if (!data) {
        // Still show a generic notification so the push isn't silently swallowed
        await self.registration.showNotification('New Notification', {
            body: 'You have a new update.',
            icon: '/static/users/images/adminlogo.jpg',
            badge: '/static/users/images/adminlogo.jpg',
            tag: 'generic-push',
            data: { url: '/' }
        });
        return;
    }

    const options = {
        body: data.message || '',
        icon: '/static/users/images/adminlogo.jpg',
        badge: '/static/users/images/adminlogo.jpg',
        vibrate: [100, 50, 100],
        // tag groups same-title notifications — new one replaces old instead of stacking
        tag: data.tag || (data.category ? `notif-${data.category}` : 'notif-general'),
        renotify: true,           // vibrate/sound even when replacing same tag
        requireInteraction: false,
        timestamp: data.timestamp ? new Date(data.timestamp).getTime() : Date.now(),
        actions: data.action_url ? [
            { action: 'open', title: 'View' },
            { action: 'dismiss', title: 'Dismiss' }
        ] : [],
        data: {
            url: data.action_url || '/',
            notifId: data.notif_id || null,
            category: data.category || 'general',
        }
    };

    try {
        await self.registration.showNotification(data.title || 'Notification', options);
    } catch (e) {
        console.error('[SW] showNotification failed:', e);
    }

    // Broadcast to all open clients so the badge/panel updates without waiting for next poll
    broadcastToClients({ type: 'PUSH_RECEIVED', category: data.category });
}


// ─── Notification Click ───────────────────────────────────────────────────────

self.addEventListener('notificationclick', function (event) {
    event.notification.close();

    const action = event.action;   // 'open', 'dismiss', or '' (body click)
    const notifData = event.notification.data || {};
    const targetUrl = notifData.url || '/';

    if (action === 'dismiss') return;

    event.waitUntil(handleNotificationClick(targetUrl, notifData));
});

async function handleNotificationClick(targetUrl, notifData) {
    const allClients = await self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true
    });

    // Find an exact-origin match — avoid matching unrelated tabs via includes()
    const origin = new URL(self.registration.scope).origin;
    let bestClient = null;

    for (const client of allClients) {
        try {
            const clientOrigin = new URL(client.url).origin;
            if (clientOrigin === origin) {
                bestClient = client;
                // Prefer a client already on the target URL
                if (client.url === targetUrl || client.url.endsWith(targetUrl)) break;
            }
        } catch (e) {
            // Malformed client URL — skip
        }
    }

    if (bestClient) {
        // Navigate the existing tab to target then focus it
        await bestClient.navigate(targetUrl).catch(() => { });
        await bestClient.focus().catch(() => { });
    } else if (self.clients.openWindow) {
        // No matching tab — open a new one
        await self.clients.openWindow(targetUrl);
    }

    // Tell all clients to mark this notification read in the UI
    if (notifData.notifId) {
        broadcastToClients({ type: 'MARK_READ', notifId: notifData.notifId });
    }
}


// ─── Notification Close ───────────────────────────────────────────────────────

self.addEventListener('notificationclose', function (event) {
    // User explicitly dismissed — tell clients to just refresh count, not animate
    broadcastToClients({ type: 'NOTIF_DISMISSED' });
});


// ─── Subscription Renewal ─────────────────────────────────────────────────────
// Fires when the browser rotates push credentials (e.g. after browser update).
// Without this, push silently breaks until the user revisits the page.

self.addEventListener('pushsubscriptionchange', function (event) {
    event.waitUntil(renewSubscription(event));
});

async function renewSubscription(event) {
    try {
        const newSubscription = await self.registration.pushManager.subscribe(
            event.oldSubscription
                ? { userVisibleOnly: true, applicationServerKey: event.oldSubscription.options.applicationServerKey }
                : { userVisibleOnly: true }
        );

        // Re-sync with server — fetch CSRF from a client cookie if possible
        const csrfToken = await getCSRFFromClient();

        await fetch('/api/notifications/subscribe/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(csrfToken && { 'X-CSRFToken': csrfToken })
            },
            body: JSON.stringify({ subscription: newSubscription })
        });
    } catch (e) {
        console.error('[SW] Subscription renewal failed:', e);
        // Queue the renewal for background sync when connectivity returns
        await queueOfflineAction({ type: 'renew_subscription' });
    }
}


// ─── Background Sync — Offline Queue ─────────────────────────────────────────
// If a push came in while offline (or server was unreachable), replay on reconnect.

self.addEventListener('sync', function (event) {
    if (event.tag === 'notif-sync') {
        event.waitUntil(flushOfflineQueue());
    }
});

async function flushOfflineQueue() {
    let queue = await readQueue();
    if (!queue.length) return;

    const failed = [];
    for (const item of queue) {
        try {
            if (item.type === 'push') {
                await self.registration.showNotification(item.title, item.options);
            } else if (item.type === 'renew_subscription') {
                // Trigger a fresh subscribe on next page load via broadcast
                broadcastToClients({ type: 'RESUBSCRIBE' });
            }
        } catch (e) {
            failed.push(item);
        }
    }

    await writeQueue(failed);
}

async function queueOfflineAction(item) {
    const queue = await readQueue();
    if (queue.length >= MAX_QUEUE) queue.shift(); // drop oldest
    queue.push(item);
    await writeQueue(queue);

    // Register background sync so it replays as soon as connectivity returns
    try {
        await self.registration.sync.register('notif-sync');
    } catch (e) {
        // Background Sync not supported in this browser — silently ignore
    }
}

async function readQueue() {
    try {
        const cache = await caches.open(OFFLINE_QUEUE_KEY);
        const res = await cache.match('queue');
        return res ? await res.json() : [];
    } catch (e) {
        return [];
    }
}

async function writeQueue(queue) {
    try {
        const cache = await caches.open(OFFLINE_QUEUE_KEY);
        await cache.put('queue', new Response(JSON.stringify(queue), {
            headers: { 'Content-Type': 'application/json' }
        }));
    } catch (e) {
        console.warn('[SW] Queue write failed:', e);
    }
}


// ─── Client Messaging ─────────────────────────────────────────────────────────

function broadcastToClients(msg) {
    self.clients.matchAll({ includeUncontrolled: true }).then(clients => {
        clients.forEach(client => client.postMessage(msg));
    });
}

// Pull CSRF token from an open client's cookies via messaging
function getCSRFFromClient() {
    return new Promise(resolve => {
        self.clients.matchAll({ type: 'window' }).then(clients => {
            if (!clients.length) return resolve(null);
            const channel = new MessageChannel();
            channel.port1.onmessage = e => resolve(e.data?.csrfToken || null);
            clients[0].postMessage({ type: 'GET_CSRF' }, [channel.port2]);
            // Timeout fallback
            setTimeout(() => resolve(null), 1000);
        });
    });
}