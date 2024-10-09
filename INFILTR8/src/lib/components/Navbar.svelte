<script>
	// Imports necessary components and icons
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import * as Icon from 'flowbite-svelte-icons';
	import favicon from '$lib/images/logos/favicon.webp';
	import { slide } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { Dropdown, DropdownItem, Popover } from 'flowbite-svelte';
	import { fade } from 'svelte/transition';
	import { menuOpen } from '$lib/stores.js';

	export let open = $menuOpen || false;
	let slideMenu = false;

	export let userInitials = 'U';

	let loggedIn = false;

	// Reactive statement to track current page path
	$: currentPath = $page.url.pathname;

	onMount(async () => {});

	// Sidebar item data: each item has text, href (link), and an icon key
	const sidebarItems = [
		{ text: 'Dashboard', href: '/dashboard', icon: Icon.GlobeSolid },
		{
			text: 'Report',
			href: '/report',
			icon: Icon.NewspaperSolid
		},
		{ text: 'Analysis', href: '/analysis', icon: Icon.BookSolid },
		{
			text: 'Project',
			href: '/project',
			icon: Icon.DatabaseSolid
		}
	];

	// Navigation links for User Profile
	const userLinks = [{ text: 'Settings', href: '/settings', icon: Icon.UserSettingsSolid }];

	function toggleMenu() {
		if (open == true) {
			open = false;
			slideMenu = false;
			$menuOpen = false;
		} else {
			open = true;
			$menuOpen = true;
		}
	}
</script>

<!-- Main container for the sidebar -->
{#if open == true}
	<aside
		id="logo-sidebar"
		class="flex-0 fixed left-0 top-0 z-40 h-screen w-52 -translate-x-full border-r border-gray-200 bg-slate-200 pt-4 transition-transform sm:translate-x-0 dark:border-gray-700 dark:bg-gray-800"
		aria-label="Sidebar"
	>
		<div class="flex flex-row items-start">
			<a href="/">
				<img src={favicon} alt="INFILTR8" class="mb-4 ml-2 mr-auto w-8 rounded drop-shadow-xl" />
			</a>

			<h1 class="oswald ml-2 mr-auto flex-grow text-2xl font-bold text-gray-900 dark:text-white">
				INFILTR8
			</h1>
			{#if userInitials != undefined}
				<button class="mr-1 rounded-lg bg-blue-100 p-2" aria-label="" in:fade={{ duration: 500 }}>
					<h1 class="text-sm font-bold text-blue-600 dark:text-blue-400">
						{userInitials}
					</h1>
				</button>
				<Popover
					class="min-w-36 text-center"
					placement="bottom"
					strategy="fixed"
					trigger="hover"
					title="Placeholder"
					transition={slide}
				>
					<div class="flex flex-col">
						{#each userLinks as link}
							<a
								href={link.href}
								class="text-gray-90 inline-flex rounded-lg py-1 pl-2 hover:bg-gray-100 hover:text-black dark:hover:bg-gray-700 dark:hover:text-white"
							>
								<svelte:component this={link.icon} class="my-auto mr-2" size="lg" />
								{link.text}
							</a>
						{/each}
					</div>
				</Popover>
			{/if}
			<button
				class="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
				aria-label="Close sidebar"
				on:click={toggleMenu}
			>
				<Icon.CaretLeftSolid size="lg" class="h-5 w-5 text-gray-500 dark:text-gray-400" />
			</button>
		</div>
		<hr class="mb-2"/>
		<div class="flex h-full flex-col overflow-y-auto bg-slate-100 dark:bg-gray-800">
			<!-- List of navigation items -->
			<ul class="space-y-2 font-medium">
				{#each sidebarItems as item}
					<li>
						<!-- Navigation link -->
						<a
							href={item.href}
							class="group flex items-center rounded-lg p-2 text-gray-900 hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700 "
						>
							<!-- Dynamic icon rendering using svelte:component -->

							<svelte:component
								this={item.icon}
								class="pointer-events-none h-5 w-5 flex-shrink-0 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-white"
							/>
							<!-- Text label for the navigation item -->
							<span class="ms-3 flex-1 whitespace-nowrap {currentPath == item.href ? 'text-primary-800 dark:text-primary-800' : ''}">{item.text}</span>
						</a>
					</li>
				{/each}
			</ul>
			<hr class="mt-2" />
			{#if loggedIn}
				<a
					data-sveltekit-preload-data="tap"
					href="/logout"
					class="group flex items-center rounded-lg p-2 text-gray-900 hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700"
				>
					<Icon.LockSolid
						class="pointer-events-none h-5 w-5 flex-shrink-0 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-white"
					/>
					<span class="ms-3 flex-1 whitespace-nowrap text-red-600">Logout</span>
				</a>
			{:else}
				<a
					data-sveltekit-preload-data="tap"
					href="/login"
					class="group flex items-center rounded-lg p-2 text-gray-900 hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700"
				>
					<Icon.LockOpenSolid
						class="pointer-events-none h-5 w-5 flex-shrink-0 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-white"
					/>
					<span class="ms-3 flex-1 whitespace-nowrap text-green-600">Login</span>
				</a>
			{/if}
		</div>
	</aside>
{:else}
	<div
		class="fixed z-50"
		aria-label="Sidebar button"
		role="button"
		tabindex="0"
		on:mouseenter={() => (slideMenu = true)}
		on:mouseleave={() => (slideMenu = false)}
	>
		<button
			class="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
			aria-label="Open sidebar"
			on:click={toggleMenu}
		>
			<Icon.DotsVerticalOutline size="xl" class="text-gray-500 dark:text-gray-400" />
		</button>
		{#if slideMenu}
			<div
				class="z-10 mt-1 flex h-full flex-col overflow-y-auto rounded-r border-y-2 border-r-2 bg-slate-100 px-3 pb-3 pt-3 dark:border-gray-800 dark:bg-gray-800"
				transition:slide={{ duration: 300, easing: quintOut }}
			>
				<div class="flex flex-row items-start">
					<img src={favicon} alt="INFILTR8" class="mb-4 ml-2 mr-auto w-8 rounded drop-shadow-xl" />
					<h1
						class="oswald ml-2 mr-auto flex-grow text-2xl font-bold text-gray-900 dark:text-white"
					>
						INFILTR8
					</h1>
					{#if userInitials != undefined}
						<button
							class="ml-4 mr-1 rounded-lg bg-blue-100 p-2"
							aria-label=""
							in:fade={{ duration: 500 }}
						>
							<h1 class="text-sm font-bold text-blue-600 dark:text-blue-400">
								{userInitials}
							</h1>
						</button>
						<Popover
							class="min-w-36 text-center"
							placement="bottom"
							strategy="fixed"
							trigger="hover"
							title="Placeholder"
							transition={slide}
						>
							<div class="flex flex-col">
								{#each userLinks as link}
									<a
										href={link.href}
										class="text-gray-90 inline-flex rounded-lg py-1 pl-2 hover:bg-gray-100 hover:text-black dark:hover:bg-gray-700 dark:hover:text-white"
									>
										<svelte:component this={link.icon} class="my-auto mr-2" size="lg" />
										{link.text}
									</a>
								{/each}
							</div>
						</Popover>
					{/if}
				</div>
				<hr class="mb-2"/>
				<!-- List of navigation items -->
				<ul class="space-y-2 font-medium">
					{#each sidebarItems as item}
						<li>
							<!-- Navigation link -->
							<a
								href={item.href}
								class="group flex items-center rounded-lg p-2 text-gray-900 hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700"
							>
								<!-- Dynamic icon rendering using svelte:component -->
								<svelte:component
									this={item.icon}
									class="pointer-events-none h-5 w-5 flex-shrink-0 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-white"
								/>
								<!-- Text label for the navigation item -->
								<span class="ms-3 flex-1 whitespace-nowrap {currentPath == item.href ? 'text-primary-800 dark:text-primary-800' : ''}">{item.text}</span>
							</a>
						</li>
					{/each}
				</ul>
				<hr class="mt-2" />
				{#if loggedIn}
					<a
						data-sveltekit-preload-data="tap"
						href="/logout"
						class="group flex items-center rounded-lg p-2 text-gray-900 hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700"
					>
						<Icon.LockSolid
							class="pointer-events-none h-5 w-5 flex-shrink-0 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-white"
						/>
						<span class="ms-3 flex-1 whitespace-nowrap text-red-600">Logout</span>
					</a>
				{:else}
					<a
						data-sveltekit-preload-data="tap"
						href="/login"
						class="group flex items-center rounded-lg p-2 text-gray-900 hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700"
					>
						<Icon.LockOpenSolid
							class="pointer-events-none h-5 w-5 flex-shrink-0 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-white"
						/>
						<span class="ms-3 flex-1 whitespace-nowrap text-green-600">Login</span>
					</a>
				{/if}
			</div>
		{/if}
	</div>
{/if}

<style>
	@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@200..700&display=swap');

	.oswald {
		font-family: 'Oswald', sans-serif;
		font-weight: 200;
	}
</style>
