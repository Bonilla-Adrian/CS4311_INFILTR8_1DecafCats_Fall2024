// src/stores/session.js
import { writable } from 'svelte/store';

// $: $session = session.subscribe(($session) => {
//     loggedIn = $session.logged_in;
//     userInitials = $session.logged_in ? $session.username[0].toUpperCase() : 'U';    ---> used to get the values from session.
// });                                                                                      good for components that only mount once, onmount unusable here (i.e. navbar)

export const session = writable({
    logged_in: false,
    username: '',
    session_id: null
});

// Fetch session status from the server
export async function checkSession() {
    const response = await fetch('/flask-api/check_session',{method: 'GET',});
    const result = await response.json();
    session.set({
        logged_in: result.logged_in,
        username: result.username || '',
        session_id: result.session_id
    });
    console.log(result.status, result.username, result.session_id)
}