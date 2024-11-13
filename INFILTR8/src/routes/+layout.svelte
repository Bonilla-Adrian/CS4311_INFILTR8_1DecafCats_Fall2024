<script>
	import '../app.css';
	import Navbar from '$lib/components/Navbar.svelte';
	import Darkmode from '$lib/components/Darkmode.svelte';
	import Colorblind from '$lib/components/Colorblind.svelte';
	import { menuOpen, darkMode } from '$lib/stores.js';
	import Toast from '$lib/components/Toast.svelte';
	import Notifications from '$lib/components/Notifications.svelte';
	import { session, checkSession } from '$lib/stores/session.js';
	import { onMount } from 'svelte';

	// Ensure dark mode class is applied on client-side only
	onMount(() => {
		darkMode.subscribe((value) => {
			if (value) {
				document.documentElement.classList.add('dark');
			} else {
				document.documentElement.classList.remove('dark');
			}
		});

		// Check session state when the component mounts
		checkSession();
	});
</script>

<svelte:head>
	<title>INFILTR8</title>
</svelte:head>

<!-- Toast notifications for temporary alerts -->
<Toast />

<div class="fixed right-0 z-50 flex items-center justify-items-center gap-3 pr-3 pt-2">
	<!-- Notifications Bell -->
	<Notifications />
	<!-- Darkmode Toggle -->
	<Darkmode showIcon={true} />
	<!-- Colorblind Toggle -->
	<Colorblind showIcon={true} />
</div>

<div class="app flex h-screen bg-gradient-to-r bg-white dark:from-gray-600 dark:to-slate-800">
	<Navbar />
	<div class={`flex-1 p-4 transition-all duration-300 ${$menuOpen ? 'ml-64' : ''} mt-10`}>
		<main>
			<slot />
		</main>
	</div>
</div>



<style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: fit-content;
	}
</style>
