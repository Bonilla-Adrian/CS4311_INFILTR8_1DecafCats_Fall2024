<script>
  import { onMount } from 'svelte';
  import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';
  import { Label, Select, Button } from 'flowbite-svelte';
  import { darkMode, colorblindMode } from '$lib/stores.js'; // Import dark mode store


  let selectedColorMode = $colorblindMode;
  let selectedFontSize = "Regular"; // Default font size
  let selectedTheme = "light"; // Default theme selection

  let currentUser = ''
    // gets username
    async function checkSession(){
        try{
            const response = await fetch('/flask-api/check_session',{
                method: 'GET',
                credentials: 'include'
            });
            if (response.ok){
                const sessionData = await response.json();
                if (sessionData.logged_in){
                    currentUser = sessionData.username;
                }else{
                    console.error("User is not logged in");
                }
            } else{
                console.error("Failed to fetch session data");
            }

        }catch (error){
            console.error("Error checking session:", error);
        }
    }

  const colorModes = [
    { value: 'Normal', name: "Normal" },
    { value: 'Protanopia', name: "Protanopia" },
    { value: 'Deuteranopia', name: "Deuteranopia" },
  ];

  const fontSizes = [
    { value: 'Small', name: "Small" },
    { value: 'Regular', name: "Regular" },
    { value: 'Large', name: "Large" },
  ];

  const themes = [
    { value: 'Light', name: "Light" },
    { value: 'Dark', name: "Dark" },
  ];

  onMount(() => {
    if (typeof window !== 'undefined') {
      // Fetch and apply font size from localStorage
      const savedFontSize = localStorage.getItem("font-size") || "Regular";
      applyFontSize(savedFontSize);
      selectedFontSize = savedFontSize;

      // Fetch and apply theme from localStorage
      const savedTheme = localStorage.getItem('color-theme') || "Light";
      selectedTheme = savedTheme.charAt(0).toUpperCase() + savedTheme.slice(1); // Capitalize first letter
    }

    // Subscribe to the darkMode store to sync selectedTheme when dark mode is toggled
    darkMode.subscribe((value) => {
      selectedTheme = value ? 'Dark' : 'Light';
    });

    colorblindMode.subscribe((value) => {
      if (typeof window !== 'undefined') {
      // Save the current colorblind mode to localStorage
      localStorage.setItem("colorblind-mode", value);
      }
    });
    checkSession();
  });

  function applyFontSize(size) {
    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      if (size === "Small") {
        root.style.fontSize = "14px";
      } else if (size === "Large") {
        root.style.fontSize = "18px";
      } else {
        root.style.fontSize = "16px";
      }
      localStorage.setItem("font-size", size);
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
                    username: currentUser,  // Dummy username for now
                    action: 'Settings click',
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

  // Function to reset all settings to their defaults
  function updateTheme(theme) {
    selectedTheme = theme;
    darkMode.set(theme === 'Dark');
    localStorage.setItem('color-theme', theme.toLowerCase()); // Save the selected theme
  }

  function resetSettings() {
    selectedColorMode = "normal";
    selectedFontSize = "Regular";
    selectedTheme = "Light";
    darkMode.set(false); // Reset to light mode

    if (typeof window !== 'undefined') {
      localStorage.removeItem("font-size");
      localStorage.removeItem("color-theme");
    }

    applyFontSize("Regular");
    updateTheme("Light");
    colorblindMode.set("Normal");
  }

  $: applyFontSize(selectedFontSize);
</script>

<div class="min-h-screen flex flex-col justify-start items-center">
  <h1 class="font-bold text-xl dark:text-white mt-6">Accessibility Options</h1>
  
  <div class="flex-grow w-full max-w-5xl p-6">
    <div id="left" class="w-full h-full">
      <div id="table" class="my-6">
        <Table noborder={true} shadow>
          <TableHead class="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-900 dark:text-gray-400">
            <TableHeadCell>Setting</TableHeadCell>
            <TableHeadCell>Description</TableHeadCell>
            <TableHeadCell class="text-right px-6 w-1/3">Option</TableHeadCell>
          </TableHead>

          <TableBody>
            <!-- Colorblind Option -->
            <TableBodyRow>
              <TableBodyCell>Color mode:</TableBodyCell>
              <TableHeadCell>Colorblind options</TableHeadCell>
              <TableBodyCell class="text-right px-6 w-1/3">
                <Label>
                  Select an option
                  <Select items={colorModes} bind:value={$colorblindMode} on:change={() => logButtonClick('Color mode click')} />
                </Label>
              </TableBodyCell>
            </TableBodyRow>

            <!-- Font Size Option -->
            <TableBodyRow>
              <TableBodyCell>Text size:</TableBodyCell>
              <TableHeadCell>Size of the font on the website</TableHeadCell>
              <TableBodyCell class="text-right px-6 w-1/3">
                <Label>
                  Select an option
                  <Select items={fontSizes} bind:value={selectedFontSize} on:change={() => applyFontSize(selectedFontSize)} on:change={() => logButtonClick('Font size click')} />
                </Label>
              </TableBodyCell>
            </TableBodyRow>

            <!-- Theme Option -->
            <TableBodyRow>
              <TableBodyCell>Theme:</TableBodyCell>
              <TableHeadCell>Light mode or Dark mode</TableHeadCell>
              <TableBodyCell class="text-right px-6 w-1/3">
                <Label>
                  Select an option
                  <Select items={themes} bind:value={selectedTheme} on:change={() => updateTheme(selectedTheme)} on:change={() => logButtonClick('Theme click')} />
                </Label>
              </TableBodyCell>
            </TableBodyRow>

            <!-- Reset Button Row -->
            <TableBodyRow>
              <TableBodyCell colspan="2"></TableBodyCell> <!-- Left side intentionally left blank -->
              <TableBodyCell class="text-right px-6 w-1/3">
                <Button color="danger" on:click={resetSettings} on:click={() => logButtonClick('Reset click')}>Reset to Defaults</Button>
              </TableBodyCell>
            </TableBodyRow>
          </TableBody>
        </Table>
      </div>    
    </div>
  </div> 
</div>
