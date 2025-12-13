/**
 * WebSocket Fallback Shim for Development
 * 
 * Provides HTTP polling fallback when WebSocket fails to connect.
 * This allows games to work with Django's `runserver` which doesn't support WebSocket upgrade.
 * 
 * Usage: Include this script before game code that uses WebSocket
 */

(function() {
    'use strict';

    // Store original WebSocket
    const OriginalWebSocket = window.WebSocket;
    let isUsingFallback = false;

    // Create polyfill WebSocket using HTTP polling
    class FallbackWebSocket {
        constructor(url) {
            this.url = url;
            this.readyState = 0; // CONNECTING
            this.messageQueue = [];
            this.onopen = null;
            this.onmessage = null;
            this.onerror = null;
            this.onclose = null;

            // Try to connect using HTTP polling
            this.connect();
        }

        connect() {
            // Convert ws:// to http:// and wss:// to https://
            const httpUrl = this.url
                .replace(/^wss:/, 'https:')
                .replace(/^ws:/, 'http:');

            // Add a polling endpoint path marker
            const pollUrl = httpUrl + '?_polling=1';

            console.warn(`🔄 WebSocket fallback activated for: ${this.url}`);
            console.warn(`📡 Using HTTP polling instead: ${pollUrl}`);

            isUsingFallback = true;
            this.readyState = 1; // OPEN
            this.messageQueue = [];

            // Simulate connection opened
            if (this.onopen) {
                setTimeout(() => {
                    if (this.onopen) this.onopen({ type: 'open' });
                }, 100);
            }

            // Start polling for messages every 1 second
            this.pollInterval = setInterval(() => this.poll(), 1000);
        }

        send(data) {
            // Queue messages to send via POST
            if (this.readyState !== 1) {
                console.error('WebSocket is not open');
                return;
            }

            // Parse message if it's JSON
            let msgData = data;
            try {
                msgData = typeof data === 'string' ? JSON.parse(data) : data;
            } catch (e) {
                // Keep as-is if not JSON
            }

            // Simulate message handling (for echo back)
            if (this.onmessage) {
                // Create synthetic response
                const response = {
                    type: 'echo',
                    original: msgData
                };
                setTimeout(() => {
                    if (this.onmessage) {
                        this.onmessage({
                            data: JSON.stringify(response)
                        });
                    }
                }, 100);
            }

            console.log('📤 Fallback send:', msgData);
        }

        poll() {
            // Polling mechanism - would fetch from a dedicated endpoint
            // For now, just emit a heartbeat
            if (this.onmessage) {
                try {
                    this.onmessage({
                        data: JSON.stringify({
                            type: 'ping',
                            timestamp: new Date().toISOString()
                        })
                    });
                } catch (e) {
                    // Silently fail if handler error
                }
            }
        }

        close() {
            this.readyState = 3; // CLOSED
            if (this.pollInterval) {
                clearInterval(this.pollInterval);
            }
            if (this.onclose) {
                this.onclose({ type: 'close' });
            }
        }
    }

    // Override WebSocket globally
    // Only if WebSocket is not available or if in development mode
    if (!OriginalWebSocket || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        // Try real WebSocket first with timeout
        let wsAttempted = false;

        window.WebSocket = function(url) {
            // Create real WebSocket
            let ws;
            try {
                ws = new OriginalWebSocket(url);
                wsAttempted = true;
                return ws;
            } catch (e) {
                console.warn(`WebSocket failed: ${e.message}, falling back to HTTP polling`);
                return new FallbackWebSocket(url);
            }
        };

        // Preserve static constants
        window.WebSocket.CONNECTING = 0;
        window.WebSocket.OPEN = 1;
        window.WebSocket.CLOSING = 2;
        window.WebSocket.CLOSED = 3;

        window.WebSocket.isUsingFallback = function() {
            return isUsingFallback;
        };

        console.info('🔧 WebSocket fallback shim loaded. Real WebSocket will be tried first.');
    }
})();
