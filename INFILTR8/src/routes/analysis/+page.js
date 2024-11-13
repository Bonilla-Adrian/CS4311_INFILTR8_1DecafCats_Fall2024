// src/routes/dashboard/+page.js
import { protectRoute } from '$lib/utils/auth';

/** @type {import('./$types').PageLoad} */
export async function load({ fetch }) {
    // Use the shared protectRoute function
    const authResult = await protectRoute(fetch);

    // If redirect response is returned, pass it back
    if (authResult?.status === 302) {
        return authResult;
    }

    // Otherwise, return props
    return {
        props: authResult
    };
}
