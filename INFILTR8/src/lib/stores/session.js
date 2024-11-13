// src/stores/session.js
import { writable } from 'svelte/store';

export const session = writable({
    logged_in: false,
    username: '',
    session_id: null
});

// Fetch session status from the server
export async function checkSession(fetch = window.fetch) {  // Default to global fetch if none provided
    const response = await fetch('/flask-api/check_session', {
        method: 'GET',
        credentials: 'include'
    });
    const result = await response.json();
    session.set({
        logged_in: result.logged_in,
        username: result.username || '',
        session_id: result.session_id
    });
    console.log(result.status, result.username, result.session_id);
}
