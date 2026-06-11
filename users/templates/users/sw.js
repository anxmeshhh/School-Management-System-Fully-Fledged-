self.addEventListener('push', function(event) {
    if (event.data) {
        try {
            const data = event.data.json();
            const options = {
                body: data.message,
                icon: '/static/users/images/adminlogo.jpg',
                badge: '/static/users/images/adminlogo.jpg',
                vibrate: [100, 50, 100],
                data: {
                    url: data.action_url || '/'
                }
            };
            
            event.waitUntil(
                self.registration.showNotification(data.title, options)
            );
        } catch (e) {
            console.error('[SW] Push event error', e);
        }
    }
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    // This looks to see if the current window is already open and focuses it
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(windowClients => {
            for (var i = 0; i < windowClients.length; i++) {
                var client = windowClients[i];
                if (client.url.includes(event.notification.data.url) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow && event.notification.data.url) {
                return clients.openWindow(event.notification.data.url);
            }
        })
    );
});
