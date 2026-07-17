/**
 * PWA install prompt — shown on login/signup pages.
 *
 * Android/Chrome-based browsers support `beforeinstallprompt`, so there we can
 * show a real "Install" button that triggers the native one-tap install.
 * iOS Safari has no programmatic install API at all (Apple does not expose
 * beforeinstallprompt or any equivalent) — the only way to install there is
 * the manual Share -> "Add to Home Screen" flow, so that's what we show.
 */
(function () {
    'use strict';

    function isStandalone() {
        return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    }

    function isIOS() {
        return /iphone|ipad|ipod/i.test(navigator.userAgent) && !window.MSStream;
    }

    function registerServiceWorker() {
        if (!('serviceWorker' in navigator)) return;
        navigator.serviceWorker.register('/sw.js').catch(function (e) {
            console.warn('[PWA] Service worker registration failed:', e);
        });
    }

    var SNOOZE_KEY = 'pwa_install_snoozed_until';

    function isSnoozed() {
        var until = localStorage.getItem(SNOOZE_KEY);
        return !!until && Date.now() < parseInt(until, 10);
    }

    function snooze(days) {
        localStorage.setItem(SNOOZE_KEY, String(Date.now() + days * 24 * 60 * 60 * 1000));
    }

    function showModal(bodyHtml, installLabel, onInstallClick) {
        if (document.getElementById('pwaInstallOverlay')) return;

        var overlay = document.createElement('div');
        overlay.id = 'pwaInstallOverlay';
        overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:99999;' +
            'display:flex;align-items:center;justify-content:center;padding:20px;font-family:sans-serif;';

        var box = document.createElement('div');
        box.style.cssText = 'background:#fff;border-radius:16px;max-width:380px;width:100%;padding:28px 24px;' +
            'text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.3);';

        box.innerHTML =
            '<div style="font-size:44px;margin-bottom:12px;">📲</div>' +
            '<h3 style="margin:0 0 10px;color:#00a651;font-size:1.25rem;font-family:inherit;">Install this App</h3>' +
            '<div style="color:#495057;font-size:0.95rem;line-height:1.5;margin-bottom:20px;">' + bodyHtml + '</div>' +
            '<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;">' +
                '<button id="pwaInstallYes" style="background:#00a651;color:#fff;border:none;padding:10px 22px;' +
                    'border-radius:8px;font-weight:600;cursor:pointer;font-size:0.95rem;">' + installLabel + '</button>' +
                '<button id="pwaInstallLater" style="background:#f1f3f5;color:#495057;border:none;padding:10px 22px;' +
                    'border-radius:8px;font-weight:600;cursor:pointer;font-size:0.95rem;">Not now</button>' +
            '</div>';

        overlay.appendChild(box);
        document.body.appendChild(overlay);

        document.getElementById('pwaInstallLater').addEventListener('click', function () {
            snooze(7);
            overlay.remove();
        });
        document.getElementById('pwaInstallYes').addEventListener('click', function () {
            overlay.remove();
            if (onInstallClick) onInstallClick();
        });
    }

    var deferredPrompt = null;

    window.addEventListener('beforeinstallprompt', function (e) {
        e.preventDefault();
        deferredPrompt = e;
        if (isStandalone() || isSnoozed()) return;
        showModal(
            'Add this app to your home screen for quick, full-screen access — just like a native app.',
            'Install',
            function () {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.finally(function () { deferredPrompt = null; });
            }
        );
    });

    function maybeShowIOSPrompt() {
        if (!isIOS() || isStandalone() || isSnoozed() || deferredPrompt) return;
        showModal(
            'To install: tap the <strong>Share</strong> icon <span style="font-size:1.1em;">⬆️</span> ' +
            'in Safari’s toolbar, then choose <strong>"Add to Home Screen"</strong>.',
            'Got it',
            null
        );
    }

    document.addEventListener('DOMContentLoaded', function () {
        registerServiceWorker();
        // beforeinstallprompt (Android/Chrome) is event-driven and may fire any time;
        // iOS has no such event, so check for it explicitly after a short delay.
        setTimeout(maybeShowIOSPrompt, 1500);
    });
})();
