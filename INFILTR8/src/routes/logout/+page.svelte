<script>
    import { session } from '../../lib/stores/session';
    import { goto } from '$app/navigation'
    import { onMount } from 'svelte';

    async function logoutUser() {
        const response = await fetch('/flask-api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            session.set({ logged_in: false, username: '' }); // Reset session store
            console.log("Logged out successfully");
            goto('/login');
        } else {
            console.error('Failed to logout');
        }
    }

    onMount(() => {
        logoutUser(); // Check session on page load
    });

</script>

<p>Logging out...</p>
