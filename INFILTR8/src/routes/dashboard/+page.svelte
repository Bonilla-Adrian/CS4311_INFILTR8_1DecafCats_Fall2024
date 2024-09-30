<script>
  // Import Flowbite components and icons
  import { Dropzone } from 'flowbite-svelte';
  import { Heading, P, Span } from 'flowbite-svelte';
  import { GradientButton } from 'flowbite-svelte';
  import { Progressbar } from 'flowbite-svelte';
  import { Listgroup } from 'flowbite-svelte';
  import { Alert } from 'flowbite-svelte';
  import { InfoCircleSolid } from 'flowbite-svelte-icons';

  let simpleList = ['Test1'];

  // Initialize the array to hold file names
  let value = [];

  // Define color schemes for accessibility and dark mode
  let selectedScheme = 'Default';  // Default scheme

  // Define dynamic color schemes for light and dark mode
  let colorSchemes = {
    'Default': {
      bg: 'bg-white dark:bg-gray-900', text: 'text-black dark:text-white', primary: 'blue', danger: 'red', success: 'green', warning: 'yellow',
    },
    'BlueYellow': {
      bg: 'bg-white dark:bg-gray-900', text: 'text-black dark:text-white', primary: 'blue', danger: 'yellow', success: 'blue', warning: 'yellow',
    },
    'RedBlue': {
      bg: 'bg-white dark:bg-gray-900', text: 'text-black dark:text-white', primary: 'red', danger: 'blue', success: 'red', warning: 'blue',
    }
  };

  $: currentScheme = colorSchemes[selectedScheme];

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

  // Handle input change for file uploads
  const handleChange = (event) => {
    const target = event.target;
    const files = target?.files;

    if (files && files.length > 0) {
      const file = files[0];
      const fileExtension = file.name.split('.').pop()?.toLowerCase();

      if (fileExtension === 'nessus') {
        value.push(file.name);
        value = [...value]; // Ensure reactivity in Svelte
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

<!-- Styles to apply background and text colors dynamically -->
<div class={`min-h-screen w-full flex flex-col items-start ${currentScheme.bg} ${currentScheme.text}`}>

  <!-- Dropdown for choosing color scheme -->
  <div class="my-4">
    <label for="theme-select" class="mr-2 text-gray-700 dark:text-gray-300">Choose Theme:</label>
    <select id="theme-select" bind:value={selectedScheme} class="p-2 border rounded">
        <option value="Default">Default</option>
        <option value="BlueYellow">Blue-Yellow</option>
        <option value="RedBlue">Red-Blue</option>
    </select>
  </div>

  <!-- Rest of your layout -->
  <div class="flex flex-row items-start justify-between min-h-screen w-full">
    <div class="flex-grow">
      <div class="flex flex-col items-center justify-center w-full">
      <Heading
        tag="h1"
        class="gradient heading mb-4 text-center text-3xl font-extrabold md:text-5xl lg:text-6xl"
      >
        WELCOME TO INFILTR8
      </Heading>
        <P>Please select from the following to get started on your project.</P>

        <!-- Dropzone component for file uploads -->
        <Dropzone
          id="dropzone"
          class="w-96 mb-2"
          on:drop={dropHandle}
          on:dragover={(event) => {
            event.preventDefault();
          }}
          on:change={handleChange}>
          <svg aria-hidden="true" class="mb-3 w-10 h-10 text-gray-400" fill="none" stroke="currentColor"
            viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
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
            <GradientButton class={`mb-2 ${currentScheme.primary}`}>Discard All</GradientButton>
            <GradientButton class={currentScheme.primary}>Create Project</GradientButton>
          </div>

          <div class="flex flex-col justify-between w-full">
            <Listgroup items={simpleList} let:item class="flex-grow w-full">
              <!-- Dynamically adjust progress bar color based on theme -->
              <div class="mb-1 text-base font-medium text-black-700 dark:text-white-500">TEST 1</div>
              <Progressbar progress="5" color={currentScheme.primary} />
              <div class="mb-1 text-base font-medium text-black-700 dark:text-white-500">TEST 2</div>
              <Progressbar progress="10" color={currentScheme.danger} />
              <div class="mb-1 text-base font-medium text-black-700 dark:text-white-500">TEST 3</div>
              <Progressbar progress="50" color={currentScheme.success} />
              <div class="mb-1 text-base font-medium text-black-700 dark:text-white-500">TEST 4</div>
              <Progressbar progress="30" color={currentScheme.warning} />
            </Listgroup>
          </div>
        </div>
      </div>
    </div>

    <div class="relative w-90 ml-8">
      <h2 class="text-xl font-bold text-gray-700 dark:text-gray-300 my-4">Notification Center</h2>
      <!-- Notifications -->
      <div class="space-y-4">
        <!-- Default alert -->
        <Alert color={currentScheme.danger}>
          <InfoCircleSolid slot="icon" class="w-5 h-5" />
          <span class="font-medium">Default alert!</span> Change a few things up and try submitting again.
        </Alert>

        <!-- Info Alert in Blue-Yellow and Red-Blue -->
        <Alert color={currentScheme.primary}>
          <InfoCircleSolid slot="icon" class="w-5 h-5" />
          <span class="font-medium">Info alert!</span> Change a few things up and try submitting again.
        </Alert>

        <!-- Success Alert and Warning Alert using scheme -->
        <Alert color={currentScheme.success}>
          <InfoCircleSolid slot="icon" class="w-5 h-5" />
          <span class="font-medium">Success alert!</span> Operation successful!
        </Alert>

        <Alert color={currentScheme.warning}>
          <InfoCircleSolid slot="icon" class="w-5 h-5" />
          <span class="font-medium">Warning alert!</span> Proceed with caution.
        </Alert>
      </div>
    </div>
  </div>
</div>
