/**
 * Enterprise Auth Handler
 * Automatically syncs Firebase ID Token with the Flask Backend Session.
 * Prevents "500 Internal Server Error" when token expires after 1 hour.
 */

document.addEventListener('DOMContentLoaded', function() {
    if (typeof firebase === 'undefined' || !firebase.auth) {
        console.error("Firebase SDK not loaded. Token sync disabled.");
        return;
    }

    firebase.auth().onIdTokenChanged(async (user) => {
        if (user) {
            // User is signed in or token was refreshed
            const idToken = await user.getIdToken();
            
            // Send new token to backend to update session cookie
            fetch('/session-login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ idToken: idToken })
            }).then(response => {
                if (!response.ok) console.warn("Failed to sync session token");
            });
        }
    });
});