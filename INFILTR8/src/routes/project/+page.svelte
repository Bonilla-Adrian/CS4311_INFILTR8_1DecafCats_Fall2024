<script>
    import IP from '$lib/IP.js';
    import { Card, Button, ButtonGroup, Listgroup, ListgroupItem } from 'flowbite-svelte';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { sendIPSToBackend, ipsAllowed, ipsDisallowed } from "$lib/stores.js"; // Import stores


    let projects = [];
    let selectedProject = null;
    let allIps = [];
    let selectedIps = [];
    
    let exploitsAllowed = [
        { id: 1, name: 'SQL Injection', selected: false },
        { id: 2, name: 'DDOS Attack', selected: false },
        { id: 3, name: 'Default Credentials', selected: false },
        { id: 4, name: 'Missing Encryption', selected: false },
        { id: 5, name: 'Unauthenticated Port Bypass', selected: false },
        { id: 6, name: 'Weak Passwords', selected: false }
    ];

    // Fetch projects from the backend on component mount
    async function fetchProjects() {
        try {
            const response = await fetch('/flask-api/all-projects');
            const data = await response.json();
            projects = data.data.map(project => ({
                ...project,
                id: project.projectId // Map projectId to id
            }));
            console.log("Projects fetched:", projects);
        } catch (error) {
            console.error('Failed to fetch projects:', error);
        }
    }

    async function fetchProjectIps(fileName) {
        try {
            const response = await fetch('/flask-api/get-all-ips', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: fileName })
            });
            const data = await response.json();

            if (response.ok) {
                allIps = data;
                ipsAllowed.set(allIps); // Store IPs in Svelte store for reactivity
                console.log("All IPs fetched:", allIps);
            } else {
                console.error("Failed to fetch IPs:", data.error);
            }
        } catch (error) {
            console.error("Error fetching IPs:", error);
        }
    }

    function loadProject(project) {
        if (!project) {
            console.error("Project is undefined.");
            return;
        }
        selectedProject = project;
        allIps = project.ips || [];
        selectedIps = [];
        console.log(`Project ${project.name} loaded.`, selectedProject);
    }

    function toggleIpSelection(ip) {
        if (selectedIps.includes(ip)) {
            // If already selected, remove it
            selectedIps = selectedIps.filter(selectedIp => selectedIp !== ip);
        } else {
            // If not selected, add it
            selectedIps = [...selectedIps, ip];
        }
        const allowedIPInstances = selectedIps.map(ipAddress => new IP(ipAddress));
        const disallowedIPInstances = allIps
        .filter(ipAddress => !selectedIps.includes(ipAddress))
        .map(ipAddress => new IP(ipAddress));

        ipsAllowed.set(allowedIPInstances);
        ipsDisallowed.set(disallowedIPInstances);

        console.log("Selected IPs for scope:", selectedIps);
        console.log("Disallowed IPs:", disallowedIPInstances.map(ip => ip.ip));
    }

    function addIPstoStore(data) {
        const ipInstances = data.map(ipAddress => new IP(ipAddress));
        ipsDisallowed.set(ipInstances);
    }

    function isValidIPv4(ip) {
        const ipv4Regex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9][0-9]?)\.(25[0-5]|2[0-4][0-9][0-9]?)$/;
        return ipv4Regex.test(ip);
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

    // Update list for reactivity
    function updateList(list) {
        if (list === $ipsAllowed) {
            ipsAllowed.set([...list]);
        } else if (list === $ipsDisallowed) {
            ipsDisallowed.set([...list]);
        } else if (list === exploitsAllowed) {
            exploitsAllowed = [...list];
        }
    }

    async function startAnalysis() {
        if (!selectedProject || !selectedProject.id) {
            alert("Please select a project with a valid ID before starting testing.");
            return;
        }
    
        const selectedExploits = exploitsAllowed.filter(exp => exp.selected).map(exp => exp.name);
    
        try {
            const response = await fetch('/flask-api/get-ips', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: selectedProject.id,         // Ensure this is defined
                    ips: allIps.join(','),                  // Convert array to comma-separated string if needed
                    exploits: selectedExploits              // Send selected exploits
                })
            });
    
            if (!response.ok) throw new Error("Failed to start project analysis.");
            
            const result = await response.json();
            console.log("Project analysis started:", result);
        } catch (error) {
            console.error('Error starting analysis:', error);
            console.log("Data sent to /flask-api/get-ips:", {
                project_id: selectedProject.id,
                ips: allIps,
                exploits: selectedExploits
            });
        }
    }

    async function logButtonClick(detail) {
        console.log("Button clicked with detail:", detail);  // For debugging
        try {
            const response = await fetch('/flask-api/log-action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: 'DummyUser',
                    action: 'Project click',
                    details: detail
                })
            });

            if (!response.ok) {
                throw new Error('Failed to log action');
            }
            const result = await response.json();
            console.log('Action logged:', result);
        } catch (error) {
            console.error('Failed to log button click:', error);
        }
    }

    onMount(() => {
        fetchProjects();
        //getIPsFromBackend();
        sendIPSToBackend();
    });
</script>

<!-- Outer wrapper to center everything -->
<div class="flex flex-col items-center justify-center">
	<!-- Main container with cards -->
	<Card class="flex min-w-fit flex-row gap-5 rounded-lg bg-gray-100 p-5 shadow-md dark:bg-gray-800">
        <!-- Show current IP list -->
        <Card class="flex-1 rounded-lg bg-white p-5 shadow-md">
            <h2 class="mb-4 text-lg font-semibold">Current Project IPS</h2>
            <Listgroup class="border-none">
                        {#each allIps as ip, index}
                            <ListgroupItem class="flex items-center gap-3 justify-between rounded-lg bg-gray-100 p-4 shadow dark:bg-gray-800 mb-4">
                                <input type="checkbox" on:change={() => toggleIpSelection(ip)} />
                                <span>{ip}</span>
                        </ListgroupItem>
                {/each}
            </Listgroup>
        </Card>

        <!-- Current Project Folder Card -->
        <Card class="flex-1 rounded-lg bg-white p-5 shadow-md">
            <h2 class="mb-4 text-lg font-semibold">Current Project Folder</h2>
            {#if selectedProject}
                <div class="flex items-center justify-between rounded-lg bg-gray-100 p-4 shadow">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-folder text-lg"></i>
                        <div>
                            <span class="block font-medium">{selectedProject.name}</span>
                            <span class="text-sm text-gray-500">{selectedProject.items} items • {selectedProject.size}</span>
                        </div>
                    </div>
                    <span class="text-gray-500">⋮</span>
                </div>
            {/if}
        </Card>

        <!-- Project Scope with Exploits Allowed -->
        <Card class="flex-1 rounded-lg bg-white p-5 shadow-md">
        <h2 class="mb-4 text-lg font-semibold">Project Scope</h2>

        <!-- Selected IPs in Scope -->
        <div class="mt-6">
            <h3 class="mb-2 text-lg font-semibold">Selected IPs</h3>
            <Listgroup class="border-none">
                {#each selectedIps as ip}
                    <ListgroupItem class="flex items-center gap-3 justify-between rounded-lg bg-gray-100 p-4 shadow dark:bg-gray-800 mb-4">
                        <span>{ip}</span>
                    </ListgroupItem>
                {/each}
            </Listgroup>
        </div>            
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
                    on:click={() => loadProject(project)} on:click={() => logButtonClick(`${project.name} clicked`)}
                >
                    <div class="flex items-center gap-3">
                        <i class="fas fa-folder text-lg"></i>
                        <div>
                            <span class="block font-medium">{project.name}</span>
                            <span class="text-sm text-gray-500">{project.fileSize} items • {project.file}</span> <!-- Adjust fields as per project properties -->
                        </div>
                    </div>
                    <span class="text-gray-500">⋮</span>
                </div>
            {/each}
        </Card>

        <!-- Schedule Analysis -->
        <Card class="flex-1 rounded-lg bg-white p-5 shadow-md">
            <h3 class="mb-4 text-lg font-semibold">Schedule Analysis</h3>
            <p class="mb-4 text-sm text-gray-500">Select a time frame to schedule your analysis.</p>
            <label class="block text-sm text-gray-700 font-medium">Choose Time Frame:</label>
            <select class="mt-2 p-2 border rounded-lg w-full mb-4">
                <option value="1_hour">1 Hour</option>
                <option value="6_hours">6 Hours</option>
                <option value="12_hours">12 Hours</option>
                <option value="24_hours">24 Hours</option>
            </select>
            <button
                class="mt-2 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700"
                on:click={scheduleAnalysis}
            >
                Schedule Analysis
            </button>
        </Card>




    </Card>

	<!-- Start Testing button placed below the layout -->
	<div class="flex space-x-4">
        <button
            class="mt-6 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700"
            on:click={startAnalysis}>
            Start Testing
        </button>
    
    </div>
</div>
