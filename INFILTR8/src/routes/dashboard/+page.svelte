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
    let simpleList = ['Test1'];
    let folderName = '';
    let nessusFile;
    let possibleEntryPoints = [];
    let validEntryPoints = [];
    let nessusContent = '';
    
    // Initialize the array to hold file names
    let value = [];
    
    // Handle file drop
    const dropHandle = (event) => {
      value = [];
      event.preventDefault();
      if (event.dataTransfer && event.dataTransfer.items) {
        [...event.dataTransfer.items].forEach((item) => {
          if (item.kind === 'file') {
            const file = item.getAsFile();
            if (file) {      
              value.push(file.name);
            }
          }
        });
      } else if (event.dataTransfer && event.dataTransfer.files) {
        [...event.dataTransfer.files].forEach((file) => {
          value.push(file.name);
        });
      }
      value = [...value]; // Ensure reactivity
    };

    // Function to parse Nessus XML content
    function parseNessusFile(content) {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(content, "application/xml");

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
          // If the file is a .nessus file, add its name to the value array
          value.push(file.name);
          value = [...value]; // Ensure reactivity in Svelte
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
    </script>
    <div class="flex flex-row items-start justify-between min-h-screen w-full">
    <div class="flex-grow">

  <div class="flex flex-col items-center justify-center w-full">
    <Heading tag="h1" class="mb-4" customSize="text-3xl text-center font-extrabold  md:text-5xl lg:text-6xl">
      <Span gradient>WELCOME TO INFILTR8</Span>
    </Heading>
    <P>Please select from the following to get started on your project.</P>
  
    <!-- Dropzone component for file uploads -->
    <Dropzone
      id="dropzone"
      class='w-96 mb-2'
      on:drop={dropHandle}
      on:dragover={(event) => {
        event.preventDefault();
      }}
      on:change={handleChange}>
      <svg aria-hidden="true" class="mb-3 w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      {#if value.length === 0}
        <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
        <p class="text-xs text-gray-500 dark:text-gray-400">Only .NESSUS files allowed</p>
      {:else}
        <p>{showFiles(value)}</p>
      {/if}
    </Dropzone>
        <div class="flex flex-row justify-between w-full mt-4">
            <div class="flex flex-col mr-8">

                <GradientButton class = "mb-2" color="green">Discard All</GradientButton>
                <form on:submit|preventDefault={submit}>
                  <GradientButton color="purple" type="submit">Create Project</GradientButton>
                </form>
            </div>
            <div class="flex flex-col justify-between w-full">
            <Listgroup items={simpleList} let:item class="flex-grow w-full">
                <div class="mb-1 text-base font-medium text-blue-700 dark:text-blue-500">TEST 1</div>
                <Progressbar progress="5" color="blue" />
                <div class="mb-1 text-base font-medium text-red-700 dark:text-red-500">TEST 2</div>
                <Progressbar progress="10" color="red" />
                <div class="mb-1 text-base font-medium text-green-700 dark:text-green-500">TEST 3</div>
                <Progressbar progress="50" color="green" />
                <div class="mb-1 text-base font-medium text-yellow-700 dark:text-yellow-500">TEST 4</div>
                <Progressbar progress="30" color="yellow" />  
                <div class="mb-1 text-base font-medium text-purple-700 dark:text-purple-400">TEST 5</div>
                <Progressbar progress="70" color="purple" />
            </Listgroup> 
                </div>
            </div>
        </div>
    </div>
    <div class="relative w-90 ml-8">
        <h2 class="text-xl font-bold text-gray-700 dark:text-gray-300 my-4">Notification Center</h2>
        <!-- Notifications -->
        <div class="space-y-4">
            <Alert>
                <InfoCircleSolid slot="icon" class="w-5 h-5" />
                <span class="font-medium">Default alert!</span>
                Change a few things up and try submitting again.
            </Alert>
            <Alert color="blue">
                <InfoCircleSolid slot="icon" class="w-5 h-5" />
                <span class="font-medium">Info alert!</span>
                Change a few things up and try submitting again.
            </Alert>
            <Alert color="red">
                <InfoCircleSolid slot="icon" class="w-5 h-5" />
                <span class="font-medium">Danger alert!</span>
                Change a few things up and try submitting again.
            </Alert>
            <Alert color="green">
                <InfoCircleSolid slot="icon" class="w-5 h-5" />
                <span class="font-medium">Success alert!</span>
                Change a few things up and try submitting again.
            </Alert>
            <Alert color="yellow">
                <InfoCircleSolid slot="icon" class="w-5 h-5" />
                <span class="font-medium">Warning alert!</span>
                Change a few things up and try submitting again.
            </Alert>
            <Alert color="dark">
                <InfoCircleSolid slot="icon" class="w-5 h-5" />
                <span class="font-medium">Dark alert!</span>
                Change a few things up and try submitting again.
            </Alert>
        </div>
    </div>
  </div>

    