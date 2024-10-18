<script>
	import { BellSolid } from 'flowbite-svelte-icons';
	import { notifications } from '$lib/stores/notifications.js';
	import { onMount } from 'svelte';

	let isOpen = false;
	let unreadCount = 0;
	$: notificationMessages = $notifications;
	$: unreadCount = notificationMessages.filter((n) => n.isNew).length;

	function toggleNotifications() {
		isOpen = !isOpen;
	}
</script>

<div class="relative">
	<button class="flex items-center justify-center relative text-gray-600 dark:text-gray-400" on:click={toggleNotifications}>
		<BellSolid class="h-7 w-7 pointer-events-none text-black dark:text-white" />

		{#if unreadCount > 0}
			<span
				class="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center text-justify rounded-full bg-red-900 {unreadCount > 99 ? 'text-[7px]' : 'text-[10px]'} text-white"
			>
				<span class="pointer-events-none my-auto">
					{unreadCount > 99 ? '99+' : unreadCount}
				</span>
			</span>
		{/if}
	</button>

	{#if isOpen}
		<div class="absolute right-0 z-50 mt-2 w-80 rounded-lg bg-white shadow-lg dark:bg-gray-800">
			<div class="border-b px-4 py-3 dark:border-gray-700">
				<h3 class="text-base font-semibold text-gray-900 dark:text-white">Notifications</h3>
			</div>

			<div class="max-h-64 overflow-y-auto">
				{#each $notifications as { id, message, isNew, type, isPermanent, timestamp }}
					<div class="flex items-start gap-2 border-b px-4 py-3 dark:border-gray-700">
						<div class="flex-shrink-0">
							<BellSolid class="h-5 w-5 text-blue-600 dark:text-blue-400" />
						</div>
						<div class="flex-1">
							<p class="text-sm text-gray-800 dark:text-gray-300">{message}</p>
							<p class="text-xs text-gray-500 dark:text-gray-400">
								{new Date(timestamp).toLocaleString()}
							</p>
						</div>
						{#if isNew}
							<span class="h-2 w-2 flex-shrink-0 rounded-full bg-blue-600"></span>
						{/if}
					</div>
				{/each}
			</div>

			<div class="px-4 py-2 text-center text-sm text-gray-500 dark:text-gray-400">
				{#if $notifications.length === 0}
					No notifications available
				{/if}
			</div>
		</div>
	{/if}
</div>
