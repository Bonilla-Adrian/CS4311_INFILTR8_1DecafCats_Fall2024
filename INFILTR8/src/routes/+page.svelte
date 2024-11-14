<script>
	import { Button, Card } from 'flowbite-svelte';
	import { Heading, P, Span } from 'flowbite-svelte';
	import { goto } from '$app/navigation';
	import { session } from '$lib/stores/session.js';

	// Function to navigate based on login status
	function handleNavigation() {
		if ($session.logged_in) {
			goto('/dashboard');
		} else {
			goto('/login');
		}
	}
</script>

<main class="flex h-screen flex-col items-center justify-center text-center p-6">
	<!-- Card component to encapsulate the content -->
	<Card class="max-w-md p-6 bg-white rounded-lg shadow-lg text-center space-y-6">
		<!-- Title using Flowbite Svelte Heading component -->
		<Heading tag="h1" class="text-6xl font-extrabold text-indigo-600">
			<Span gradient>INFILTR8</Span>
		</Heading>

		<!-- Description using Flowbite Svelte Paragraph component -->
		<P class="text-lg text-gray-700 text-center">
			Welcome to <span class="font-bold">INFILTR8</span>.
		</P>

		<!-- Button using Flowbite Svelte Button component -->
		<Button color="primary" pill on:click={handleNavigation} class="w-full hover:scale-105 transition-transform duration-150">
			{#if $session.logged_in}
				Proceed to Dashboard
			{:else}
				Proceed to Login
			{/if}
		</Button>
	</Card>
</main>
