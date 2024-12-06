<script>
    // Drag and drop
    import { Dropzone } from 'flowbite-svelte';
    import { Heading, P, Span } from 'flowbite-svelte';
    import { GradientButton } from 'flowbite-svelte';
    import { Progressbar } from 'flowbite-svelte';
    import { Listgroup } from 'flowbite-svelte';
    import { Alert } from 'flowbite-svelte';
    import { InfoCircleSolid } from 'flowbite-svelte-icons';
    import { onMount } from 'svelte';
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';
    let simpleList = ['Test1'];
    let folderName = '';
    let nessusFile;
    let possibleEntryPoints = [];
    let validEntryPoints = [];
    let nessusContent = '';
    let message = "";
    let projectInfo = null;
    
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
      console.log("Parsed entry points:", possibleEntryPoints);
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

    function submit() {
      validateEntryPoints();
      const requestData = {
        folderName,
        validEntryPoints
      };
      console.log('Request Data:', requestData);
    }
    
    // Handle input change for file uploads
    const handleChange = (event) => {
        const target = event.target;
        const files = target?.files;
    
        if (files && files.length > 0) {
            const file = files[0];
            const fileExtension = file.name.split('.').pop()?.toLowerCase();
    
            if (fileExtension === 'nessus') {
                nessusFile = file;
                console.log("File selected:", nessusFile);
                uploadNessusFile();
                const reader = new FileReader();
                reader.onload = (e) => {
                    nessusContent = e.target.result;
                    parseNessusFile(nessusContent);
                    isFileReady = true;  // Set to true after parsing
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

// Uploads the Nessus file
  async function uploadNessusFile() {
    if (!nessusFile) {
      message = "Please select a file to upload.";
      return;
    }

    isLoading = true;
    const formData = new FormData();
    formData.append("file", nessusFile);

    try {
      const uploadResponse = await fetch("http://localhost:5000/flask-api/nessus-upload", {
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
    } finally {
      isLoading = false;
    }
  }

    async function createProject() {
        if (!nessusFile) {
            message = "Upload a .nessus file first.";
            console.warn(message);
            return;
        }
        if (possibleEntryPoints.length === 0) {
            message = "No entry points found in the Nessus file. Please upload a valid file.";
            console.warn(message);
            return;
        }

        const projectData = {
            folderName: nessusFile.name,
            entryPoints: possibleEntryPoints  // Pass parsed entry points
        };

        try {
            const response = await fetch("http://localhost:5000/flask-api/create-project", {
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
            } else {
                message = "Failed to create project.";
                console.error("Project creation failed with status:", response.status);
            }
        } catch (error) {
            message = "Error: " + error.message;
            console.error("Error during project creation:", error);
        }
    }
    </script>
    <div class="flex flex-row items-start justify-between min-h-screen w-full">
    <div class="flex-grow">

  <div class="flex flex-col items-center justify-center w-full">
    <Heading tag="h1" class="mb-4" customSize="text-3xl text-center font-extrabold  md:text-5xl lg:text-6xl">
      <Span gradient>WELCOME TO INFILTR8</Span>
    </Heading>
    <P>Please select from the following to get started on your project.</P>
  
    <!-- Dropzone component for file uploads -->
      <input type="file" accept=".nessus" on:change="{handleChange}" />

        <div class="flex flex-row justify-between w-full mt-4">
            <div class="flex flex-col mr-8">

                <GradientButton class = "mb-2" color="green">Discard All</GradientButton>
                <GradientButton on:click={createProject}>Create Project</GradientButton>
            </div>
            <div class="flex flex-col justify-between w-full">
                {#if projectInfo}
                        <Table color="blue" hoverable={true}>
                            <TableHead>
                                <TableHeadCell>Project Name</TableHeadCell>
                                <TableHeadCell>Project ID</TableHeadCell>
                            </TableHead>
                            <TableBody>
                                <TableBodyRow>
                                    <TableBodyCell>{projectInfo.name}</TableBodyCell>
                                    <TableBodyCell>{projectInfo.id}</TableBodyCell>
                                </TableBodyRow>
                            </TableBody>
                        </Table>
                      {/if}
                </div>            
            </div>
        </div>
    </div>
    <div class="relative w-90 ml-8">
    </div>
  </div>

    