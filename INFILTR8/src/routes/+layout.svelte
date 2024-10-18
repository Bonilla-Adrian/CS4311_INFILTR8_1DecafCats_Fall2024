<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import Navbar from '$lib/components/Navbar.svelte';
	import Darkmode from '$lib/components/Darkmode.svelte';
	import Colorblind from '$lib/components/Colorblind.svelte';
	import { menuOpen } from '$lib/stores.js';
	import { addNewNotification } from '$lib/stores/notifications.js';
	import Toast from '$lib/components/Toast.svelte';
	import Notifications from '$lib/components/Notifications.svelte';

	const mockNotifications = [
		{
			id: 1,
			message: 'Mock Notification 1',
			type: 'message',
			timestamp: '2024-01-01T12:00:00',
			new: true,
			timeout: 3000,
			isPermanent: false
		}, // Temporary
		{
			id: 2,
			message: 'Mock Notification 2',
			type: 'success',
			timestamp: '2024-01-02T13:00:00',
			new: true,
			timeout: 3000,
			isPermanent: true
		}, // Permanent
		{
			id: 3,
			message: 'Mock Notification 3',
			type: 'error',
			timestamp: '2024-01-03T14:00:00',
			new: false,
			timeout: 3000,
			isPermanent: true
		} // Permanent
	];

	onMount(() => {
		console.log('Loading mock notifications...');
		mockNotifications.forEach((notification) => {
			addNewNotification(notification); // Add each notification (temporary or permanent)
		});
		console.log('Mock notifications loaded.');
	});
</script>

<svelte:head>
	<title>INFILTR8</title>
</svelte:head>

<Toast />

<div class="fixed right-0 z-50 flex justify-items-center items-center gap-3 pr-3 pt-2">
	<!-- Notifications Bell -->
	<Notifications />
	<!-- Darkmode Toggle -->
	<Darkmode />
	<!-- Colorblind Toggle -->
	<Colorblind />
</div>

<div class="app flex h-screen bg-gray-50 dark:bg-gray-600">
	<Navbar />
	<div class={`flex-1 bg-gray-50 p-4 dark:bg-gray-600 ${$menuOpen ? 'ml-64' : ''} mt-10`}>
		<main class="">
			<slot />
		</main>
	</div>
</div>

<style>
	.app {
	  display: flex;
	  flex-direction: column;
	  min-height: 300vh;
	}
</style>
