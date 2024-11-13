<script>
    // Drag and drop
    import { Dropzone } from 'flowbite-svelte';
    import { Progressbar } from 'flowbite-svelte';
    import { Listgroup } from 'flowbite-svelte';
    import { Alert } from 'flowbite-svelte';
    import { Input } from 'flowbite-svelte';
    import { InfoCircleSolid } from 'flowbite-svelte-icons';
    import { Heading, P, Span, GradientButton } from 'flowbite-svelte';
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';
    import { getIPsFromBackend } from '$lib/stores.js'
	import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    
    let simpleList = ['Test1'];
    let folderName = '';
    
    let nessusFile;
    let message = "";
    let isLoading = true
    let ipList = []
    let projectInfo = null;
    let possibleEntryPoints = [];
    let validEntryPoints = [];
    let projects = [];
    
    // Initialize the array to hold file names
    let value = [];
    
    // Handle file drop
    const dropHandle = (event) => {
      console.log("File drop detected");
      event.preventDefault();
      if (event.dataTransfer && event.dataTransfer.files.length > 0) {
        nessusFile = event.dataTransfer.files[0];
        console.log("File selected:", nessusFile);
        uploadNessusFile();
      }
    };

    // Function to parse Nessus XML content
    function parseNessusFile(content) {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(content, "application/xml");
      possibleEntryPoints = [];

      // Example of extracting IP and port info
      const hosts = xmlDoc.getElementsByTagName("ReportHost");
      possibleEntryPoints = [];
      for (let host of hosts) {
        const ip = host.getAttribute("name");
        const reportItems = host.getElementsByTagName("ReportItem");
        for (let item of reportItems) {
          const port = item.getAttribute("port");
          const severity = item.getAttribute("severity"); // Example attribute, might need adjustment based on your Nessus file
          const pluginID = item.getAttribute("pluginID");
          const service = item.getAttribute("svc_name");

          // Collect only relevant data, e.g., open ports and severity levels
          possibleEntryPoints.push({ ip, port, severity, pluginID, service });
        }
      }
      // console.log("Parsed entry points:", possibleEntryPoints);
    }

    // Function to validate entry points based on open ports or severity levels
    function validateEntryPoints() {
      validEntryPoints = possibleEntryPoints.filter(point => {
        // Logic: Only include entries with high severity (severity level 3 or more)
        const severityThreshold = 3; // Example threshold: 3 = medium, 4 = high, 5 = critical
        const isHighSeverity = parseInt(point.severity) >= severityThreshold;

        // Logic: Only include open ports (you might need to adjust based on Nessus data for open/closed port status)
        const isValidPort = point.port > 0;

        // Combine both conditions
        return isHighSeverity && isValidPort;
      });
    }
    
    // Handle input change for file upload
    
    async function fetchProjects() {
        try {
            const response = await fetch('http://localhost:5173/flask-api/all-projects', {
                credentials: 'include'
            });
            if (response.ok) {
                const data = await response.json();
                projects = data.data; 
            } else {
                message = "Failed to fetch projects";
                console.error("Fetch error:", response.status);
            }
        } catch (error) {
            message = "Error fetching projects";
            console.error("Error fetching projects:", error);
        }
    }

    onMount(() => {
        fetchProjects();
    });

    const handleChange = (event) => {
        const target = event.target;
        const files = target?.files;
    
        if (files && files.length > 0) {
            const file = files[0];
            const fileExtension = file.name.split('.').pop()?.toLowerCase();
    
            if (fileExtension === 'nessus') {
                nessusFile = file;
                console.log("File selected:", nessusFile);
                let fetchP = uploadNessusFile()
                fetchP.then((response) => {
                  // put error handle stuff here
                  ipList = getIPsFromBackend(nessusFile.name)
                })
                const reader = new FileReader();
                reader.onload = (e) => {
                    nessusContent = e.target.result;
                    parseNessusFile(nessusContent);
                };
                reader.readAsText(file);
            } else {
                console.error('Invalid file type. Please upload a .nessus file.');
            }
        }
    };
    
    // Display the uploaded files
    const showFiles = (files) => {
      if (files.length === 1) return files[0];
      let concat = '';
      files.forEach((file) => {
        concat += file + ', ';
      });
    
      if (concat.length > 40) concat = concat.slice(0, 40);
      concat += '...';
      return concat;
    };

  async function uploadParse() {
    let fetchP = uploadNessusFile()
    await fetchP.then(ipList = getIPsFromBackend(nessusFile.name))
  }


    async function uploadNessusFile() {
        if (!nessusFile) {
            message = "Please select a file to upload.";
            return;
        }

        const formData = new FormData();
        formData.append("file", nessusFile);

        try {
            const uploadResponse = await fetch("http://localhost:5173/flask-api/nessus-upload", {
                method: "POST",
                body: formData,
            });

            if (uploadResponse.ok) {
                const result = await uploadResponse.json();
                message = "File uploaded successfully: " + result.status;
            } else {
                message = "File upload failed. Please try again.";
            }
        } catch (error) {
            message = "Upload error: " + error.message;
        }
    }

  async function createProject() {
      if (!nessusFile || document.getElementById("first_name").value === "") {
          message = "Upload a .nessus file first.";
          console.warn(message);
          return;
      }

      let ips
      await ipList.then(function(result){ips = result})
      const projectData = {
          fileName: nessusFile.name,
          name: document.getElementById("first_name").value,
          ips: ips
          // entryPoints: possibleEntryPoints  // Pass parsed entry points
      };

        try {
            const response = await fetch("http://localhost:5173/flask-api/create-project", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(projectData),
                credentials: "include"
            });

        if (response.ok) {
            const data = await response.json();
            projectInfo = { id: data.projectId, name: nessusFile.name };

            message = `Project created successfully with ID: ${data.projectId}`;
            console.log(message);
            fetchProjects(); 
        } else {
            message = "Failed to create project.";
            console.error("Project creation failed with status:", response.status);
        }
      } catch (error) {
          message = "Error: " + error.message;
          console.error("Error during project creation:", error);
      }
      goto('/project')
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
                    username: 'DummyUser',  // Dummy username for now
                    action: 'Dashboard click',
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

</script>
    
<div class="flex flex-row items-start justify-between min-h-screen w-full">
    <div class="flex-grow">
        <div class="flex flex-col items-center min-h-screen w-full p-6">
            <Heading tag="h1" class="mb-4 text-3xl font-extrabold text-center md:text-5xl lg:text-6xl">
            <Span gradient>WELCOME TO INFILTR8</Span>
            </Heading>
            <!-- Dropzone component for file uploads -->
            <div class="justify-between">
                <input type="file" accept=".nessus" on:change="{handleChange}" />
                <form >
                    <Input class="text-center" type="text" id="first_name" placeholder="Enter Project Name" required />
                </form>
            </div>
            <!-- <input bind:value={name} placeholder="Enter Project Name" /> -->
            <div class="flex flex-row justify-between w-full mt-4">
                <div class="flex flex-col mr-8">
                    <div class="relative w-90 ml-8">
                        <P class="text-center mb-8">Please select from the following to get started on your project.</P>


                        <div class="flex flex-col items-center mb-8 w-full">
                            <GradientButton class = "mb-2" color="green"on:click={() => logButtonClick('Discard All clicked')}>Discard All</GradientButton>
                            <GradientButton on:click={() => { logButtonClick('Create project clicked'); createProject(); }}>Create Project</GradientButton>           
                        </div>
                    </div>
                    <div>
                        <h2 class="text-2xl font-semibold mb-4 text-center">Project List</h2>
        
                        {#if projects.length > 0}
                            <Table hoverable={true} class="shrink">
                                <TableHead>
                                    <TableHeadCell>Project Name</TableHeadCell>
                                    <TableHeadCell>Project ID</TableHeadCell>
                                    <TableHeadCell>IPs</TableHeadCell>
                                    <TableHeadCell>Exploits</TableHeadCell>
                                </TableHead>
                                <TableBody>
                                    {#each projects as project}
                                        <TableBodyRow>
                                        <TableBodyCell>{project.projectName}</TableBodyCell>
                                        <TableBodyCell>{project.projectId}</TableBodyCell>
                                        <TableBodyCell class="text-wrap">{project.ips ? project.ips.join(', ') : ''}</TableBodyCell>
                                        <TableBodyCell>
                                        {#if Array.isArray(project.exploits)}
                                            {project.exploits.join(', ')}
                                        {:else}
                                            {project.exploits} <!-- Displays the string if it's not an array -->
                                        {/if}
                                    </TableBodyCell> 
                                    </TableBodyRow>
                                    {/each}
                                </TableBody>
                            </Table>
                        {:else if message}
                            <p class="text-center text-red-500">{message}</p>
                        {:else}
                            <p class="text-center">Loading projects...</p>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>