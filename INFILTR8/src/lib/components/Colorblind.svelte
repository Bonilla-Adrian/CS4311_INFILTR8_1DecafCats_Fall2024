<script>
  import { EyeSolid } from 'flowbite-svelte-icons';
  import { onMount } from 'svelte';
  
  let colorblindMode = "normal";  // Default: No colorblind simulation

  onMount(() => {
    colorblindMode = localStorage.getItem('colorblind-mode') || 'normal';  // Load colorblind mode from localStorage if available
    applyColorblindFilter();
  });

  let toggleColorblindMode = () => {
    if (colorblindMode === 'normal') {
      colorblindMode = 'protanopia';  // Simulate Protanopia
    } else if (colorblindMode === 'protanopia') {
      colorblindMode = 'deuteranopia';  // Simulate Deuteranopia
    } else {
      colorblindMode = 'normal';  // Go back to normal mode
    }
    localStorage.setItem('colorblind-mode', colorblindMode);  // Save the mode in localStorage
    applyColorblindFilter();  // Apply the filter based on the mode
  };

  let applyColorblindFilter = () => {
    const root = document.documentElement;

    // Reset filters for normal vision
    if (colorblindMode === 'normal') {
      root.style.filter = 'none';
    } 
    // Apply protanopia filter
    else if (colorblindMode === 'protanopia') {
      root.style.filter = 'url(#protanopia-filter)';
    } 
    // Apply deuteranopia filter
    else if (colorblindMode === 'deuteranopia') {
      root.style.filter = 'url(#deuteranopia-filter)';
    }
  };
</script>

<!-- SVG Filters for colorblind simulation -->
<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
  <filter id="protanopia-filter">
    <feColorMatrix type="matrix" values="0.56667 0.43333 0 0 0 0.55833 0.44167 0 0 0 0 0.24167 0.75833 0 0 0 0 0 1 0"></feColorMatrix>
  </filter>
  <filter id="deuteranopia-filter">
    <feColorMatrix type="matrix" values="0.625 0.375 0 0 0 0.7 0.3 0 0 0 0 0.3 0.7 0 0 0 0 0 1 0"></feColorMatrix>
  </filter>
</svg>

<!-- Button to toggle between normal, protanopia, and deuteranopia modes -->
<button on:click={toggleColorblindMode}>
  {#if colorblindMode === 'normal'}
    <EyeSolid color='black' class="h-7 w-7 pointer-events-none" />  <!-- Normal mode icon -->
  {:else if colorblindMode === 'protanopia'}
    <EyeSolid color='#ff4c4c' class="h-7 w-7 pointer-events-none" />  <!-- Protanopia mode icon -->
  {:else if colorblindMode === 'deuteranopia'}
    <EyeSolid color='#4caf50' class="h-7 w-7 pointer-events-none" />  <!-- Deuteranopia mode icon -->
  {/if}
</button>