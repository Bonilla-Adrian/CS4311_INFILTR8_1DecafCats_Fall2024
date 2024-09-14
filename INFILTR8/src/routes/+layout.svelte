<script>
	import '../app.css';
	import Navbar from '$lib/components/Navbar.svelte';
	import Darkmode from '$lib/components/Darkmode.svelte';
	import { menuOpen } from '$lib/stores.js';

</script>

<svelte:head>
	<title>INFILTR8</title>
</svelte:head>

<div class="fixed right-0 z-50 pr-3 pt-2">
	<Darkmode />
</div>

<div class="app flex h-screen bg-gray-50 dark:bg-gray-600">
	<Navbar />
	<div class={`p-4 flex-1 bg-gray-50 dark:bg-gray-600 ${$menuOpen ? 'ml-64' : ''} mt-10`}>
		<main class="">
			<slot />
		</main>
	</div>
</div>

<style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

</style>