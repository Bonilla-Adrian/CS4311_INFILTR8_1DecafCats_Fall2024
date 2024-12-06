<script>
	import { Modal, Label, Input, Textarea, Button, Toggle, Select } from 'flowbite-svelte';
	import { writable } from 'svelte/store';
	import { onMount } from 'svelte';

	export let open = false;
	export let fields = [];
	export let title = 'Add Item';
	export let actionUrl = '#';
    export let redirectable = false;
	export let redirectToNewPage = writable(false);
	export let itemName = '';

	onMount(() => {
		if (localStorage.getItem('goToNewItem')) {
			let goToNewItem = JSON.parse(localStorage.getItem('goToNewItem'));

			try {
				if (goToNewItem) {
					redirectToNewPage.set(true);
				}
			} catch (e) {
				console.log(e);
			}
		} else {
			redirectToNewPage.set(false);
			localStorage.setItem('goToNewItem', JSON.stringify(false));
		}
	});

	function updateGoToNewState() {
		localStorage.setItem('goToNewItem', JSON.stringify(redirectOnSubmit));
	}

	let redirectOnSubmit = false;
	let wordCounts = {}; // To store word counts for fields that require them

	let submitText = 'Submit';

	// Reactive update for redirection
	$: redirectOnSubmit = $redirectToNewPage;

	// Count words in the textarea input
	function countWords(input, fieldName) {
		wordCounts[fieldName] = input.trim().split(/\s+/).length;
	}

	// Ensure URLs start with http:// or https://
	function ensureHttps(inputValue, fieldName) {
		if (!inputValue.startsWith('https://') && !inputValue.startsWith('http://')) {
			const index = fields.findIndex((field) => field.name === fieldName);
			fields[index].value = `https://${inputValue}`;
		}
	}

	// Handle form submission
	async function handleSubmit() {
		const formData = new FormData();
		fields.forEach((field) => {
			formData.append(field.name, field.value);
		});

		const response = await fetch(actionUrl, {
			method: 'POST',
			body: formData
		});

		const result = await response.json();
		console.log(result);

		if (redirectOnSubmit) {
			window.location.href = `${result.location}`;
		} else {
			open = false;
			dataTableUpdateTrigger.set(true); // Trigger an update
		}
	}

	// Validity check for form submission
	$: valid = fields.every((field) => !field.required || (field.value && field.value.trim() !== ''));
</script>

<Modal {title} bind:open class="min-w-full">
	<form on:submit|preventDefault={handleSubmit}>
		{#each fields as field}
			<div class="mb-4 grid sm:grid-cols-1">
				<Label for={field.name} class="mb-1">
					{field.label}
					{#if field.required}
						<span class="text-red-600">*</span>
					{/if}
				</Label>
				{#if field.type === 'textarea'}
					<Textarea
						id={field.name}
						name={field.name}
						placeholder={field.placeholder}
						rows={field.rows || 4}
						bind:value={field.value}
						on:input={() => countWords(field.value, field.name)}
						required={field.required}
					/>
				{:else if field.type === 'email'}
					<Input
						type="email"
						id={field.name}
						name={field.name}
						placeholder={field.placeholder}
						bind:value={field.value}
						required={field.required}
					/>
				{:else if field.type === 'url'}
					<div class="relative flex items-center">
						<Input
							type="url"
							id={field.name}
							name={field.name}
							placeholder={field.placeholder}
							class="w-full"
							bind:value={field.value}
							on:blur={() => ensureHttps(field.value, field.name)}
							required={field.required}
						/>
					</div>
				{:else if field.type === 'select'}
					<div class="relative flex items-center">
						<Select
							id={field.name}
							name={field.name}
							bind:value={field.value}
							required={field.required}
						>
							{#each field.options as option}
								<option value={option.id}>{option.name}</option>
							{/each}
						</Select>
					</div>
				{:else}
					<Input
						type={field.type}
						id={field.name}
						name={field.name}
						placeholder={field.placeholder}
						bind:value={field.value}
						on:input={() => countWords(field.value, field.name)}
						required={field.required}
					/>
				{/if}
			</div>
		{/each}
		<Button type="submit" disabled={!valid} class="mr-auto mt-8 min-w-fit">
			<svg
				class="-ml-1 mr-1 h-6 w-6"
				fill="currentColor"
				viewBox="0 0 20 20"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					fill-rule="evenodd"
					d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
					clip-rule="evenodd"
				/>
			</svg>
			{submitText}
		</Button>
        {#if redirectable}
            <div class="flex">
                <Label class="-mt-[22px] ml-auto text-sm">Go to new {itemName}?</Label>
                <Toggle class="-mt-6 pl-3" bind:checked={redirectOnSubmit} on:change={updateGoToNewState}
                ></Toggle>
            </div>
        {/if}
	</form>
</Modal>
