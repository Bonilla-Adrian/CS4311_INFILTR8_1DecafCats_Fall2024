// src/lib/utils/auth.js
import { checkSession, session } from '$lib/stores/session.js';
import { get } from 'svelte/store';
import { goto } from '$app/navigation';

/** Protects a route by checking session status and redirecting if not authenticated */
export async function protectRoute(fetch) {
    // Perform session check
    await checkSession(fetch);

    const currentSession = get(session);

    if (!currentSession.logged_in) {
        // Server-side redirection
        if (typeof window === 'undefined') {
            return {
                status: 302,
                redirect: '/'
            };
        } else {
            // Client-side redirection
            goto('/');
            return;
        }
    }

    // Return props if authenticated
    return {
        username: currentSession.username
    };
}
