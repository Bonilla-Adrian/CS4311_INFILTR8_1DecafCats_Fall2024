<!--TODO add store for exploits allowed -->
<!--visual planning-->


<script>
    import IP from '$lib/IP.js';
    import { Card, Button, ButtonGroup, Listgroup, ListgroupItem, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';
    import { TrashBinSolid } from 'flowbite-svelte-icons';
    import { ipsAllowed } from '$lib/stores.js';
    import { ipsDisallowed } from '$lib/stores.js';
    import { onMount } from 'svelte';

    //should be ran once a nessus file is uploaded
    async function getIPsFromBackend() {
        try {
            const response = await fetch("/flask-api/get-all-ips", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                }
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await response.json(); // Parse JSON response
            console.log("IPs received from backend:", data);
            addIPstoStore(data); // Update the store with received IPs
        } catch (error) {
            console.error("There was an error retrieving IPs from the backend:", error);
        }
    }
  
    function addIPstoStore(data) {
        const ipInstances = data.map(ipAddress => new IP(ipAddress)); // Create IP instances
        console.log(ipInstances)
        ipsDisallowed.set(ipInstances); // Update the store with IP instances
    }

    onMount(() => {
        getIPsFromBackend();
    });

    let exploitsAllowed = [
        { id: 1, name: 'SQL Injection', selected: false },
        { id: 2, name: 'DDOS Attack', selected: false },
        { id: 3, name: 'Default Credentials', selected: false },
        { id: 4, name: 'Missing Encryption', selected: false },
        { id: 5, name: 'Unauthenticated Port Bypass', selected: false },
        { id: 6, name: 'Weak Passwords', selected: false }
    ];

    let projects = [
        { id: 1, name: 'Example 1', size: '1.42 GB', items: 49 },
        { id: 2, name: 'Example 2', size: '2.8 GB', items: 286 },
        { id: 3, name: 'Example 3', size: '84 MB', items: 52 },
        { id: 4, name: 'Example 4', size: '1.6 GB', items: 109 },
        { id: 5, name: 'Example 5', size: '1.15 GB', items: 76 },
        { id: 6, name: 'Example 6', size: '1.3 GB', items: 43 },
        { id: 7, name: 'Example 7', size: '1.6 GB', items: 109 }
    ];

    let selectedProject = null;

    function isValidIPv4(ip) {
        const ipv4Regex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return ipv4Regex.test(ip);
    }

    function handleDelete(list, index, updateList) {
        const newList = list.filter((_, i) => i !== index);
        updateList(newList);
       // logger.logUserAction(testuser,"Deleted item", `at index ${index}. New list:`, newList );
    }

    function moveUp(list, index) {
        if (index > 0) {
            [list[index - 1], list[index]] = [list[index], list[index - 1]];
            updateList(list);
        }
    }

    function moveDown(list, index) {
        if (index < list.length - 1) {
            [list[index], list[index + 1]] = [list[index + 1], list[index]];
            updateList(list);
        }
    }

    // Ensure the list is updated to trigger reactivity
    function updateList(list) {
        if (list === $ipsAllowed) {
            $ipsAllowed = [...list];
        }  else if (list === $ipsDisallowed) {
            $ipsDisallowed = [...list]
        }  else if (list === exploitsAllowed) {
            exploitsAllowed = [...list];
        }
        
    }

    function loadProject(project) {
        selectedProject = project;
        console.log(`Project ${project.name} loaded.`);
    }
</script>

<!-- Outer wrapper to center everything -->
<div class="flex flex-col items-center justify-center">
	<!-- Main container with both cards -->
	<Card class="flex min-w-fit flex-row gap-5 rounded-lg bg-gray-100 p-5 shadow-md dark:bg-gray-800">
		<!-- Current Project Folder Card -->
        <Card class="flex-1 rounded-lg bg-white p-5 shadow-md">
            <h2 class="mb-4 text-lg font-semibold">Current Project Folder</h2>
            {#if selectedProject}
                <div class="flex items-center justify-between rounded-lg bg-gray-100 p-4 shadow">
                    <div class="flex items-center gap-3">
                        <!-- Font Awesome folder icon -->
                        <i class="fas fa-folder text-lg"></i>
                        <div>
                            <span class="block font-medium">{selectedProject.name}</span>
                            <span class="text-sm text-gray-500"
                                >{selectedProject.items} items • {selectedProject.size}</span
                            >
                        </div>
                    </div>
                    <span class="text-gray-500">⋮</span>
                </div>
            {/if}
        </Card>

		<Card class="flex-1 rounded-lg bg-white p-5 shadow-md">
            <h2 class="mb-4 text-lg font-semibold">Project Scope</h2>
			<!-- Allowed IP List -->
				<h3 class="mb-2 text-lg font-semibold">IPs Allowed</h3>
            <Listgroup class="border-none">
				{#each $ipsAllowed as ip, index}
					<ListgroupItem class="flex items-center gap-3 justify-between rounded-lg bg-gray-100 p-4 shadow dark:bg-gray-800 mb-4">                  
                        <input type="checkbox" bind:checked={ip.selected} />
                        <span>{ip.ip}</span>
                        <ButtonGroup class="*:!ring-primary-700">
                            <Button size="sm mr-2" on:click={() => moveUp($ipsAllowed, index)}>⬆</Button>
                            <Button size="sm mr-2" on:click={() => moveDown($ipsAllowed, index)}>⬇</Button>             
                        </ButtonGroup >						
					</ListgroupItem>
				{/each}
			</Listgroup>
            <Button class="text-base mt-4" on:click={() => addIP()}>add ip (testing purposes only)</Button>

			<!-- Exploits Allowed -->
			<div class="mt-6">
				<h3 class="mb-2 text-lg font-semibold">Exploits Allowed</h3>
                <Listgroup class="border-none">
                    {#each exploitsAllowed as exploit, index}
                        <ListgroupItem class="flex items-center gap-3 justify-between rounded-lg bg-gray-100 p-4 shadow dark:bg-gray-800 mb-4">                  
                            <input type="checkbox" bind:checked={exploit.selected} />
                            <span>{exploit.name}</span>
                            <ButtonGroup class="*:!ring-primary-700">
                                <Button size="sm mr-2" on:click={() => moveUp(exploitsAllowed, index)}>⬆</Button>
                                <Button size="sm mr-2" on:click={() => moveDown(exploitsAllowed, index)}>⬇</Button>             
                            </ButtonGroup >						
                        </ListgroupItem>
                    {/each}
                </Listgroup>
			</div>
		</Card>

		<!-- Load Project Card -->
		<Card class="flex-1 rounded-lg bg-white p-5 shadow-md">
			<h3 class="mb-4 text-lg font-semibold">Load Project</h3>
			{#each projects as project}
				<div
					class="mb-4 flex cursor-pointer items-center justify-between rounded-lg bg-gray-100 p-4 shadow dark:bg-gray-800 mb-4"
					on:click={() => loadProject(project)}
				>
					<div class="flex items-center gap-3">
						<!-- Font Awesome folder icon -->
						<i class="fas fa-folder text-lg"></i>
						<div>
							<span class="block font-medium">{project.name}</span>
							<span class="text-sm text-gray-500">{project.items} items • {project.size}</span>
						</div>
					</div>
					<span class="text-gray-500">⋮</span>
				</div>
			{/each}
    
	    </Card>
	</Card>

	<!-- Start Testing button placed below the layout -->
	<button
		class="mt-6 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700"
		on:click={() => console.log('Start Testing')}>Start Testing</button
	>
</div>