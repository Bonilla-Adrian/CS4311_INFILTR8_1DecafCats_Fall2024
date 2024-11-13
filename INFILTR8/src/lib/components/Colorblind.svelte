<script>
  import { EyeSolid } from 'flowbite-svelte-icons';
  import { darkMode, colorblindMode } from '$lib/stores.js';
  import { onMount } from 'svelte';

  export let showIcon = true;

  onMount(() => {
    if (typeof window !== 'undefined') {
      const savedMode = localStorage.getItem('colorblind-mode') || "Normal";
      colorblindMode.set(savedMode);
    }
  });

  const toggleColorblindMode = () => {
    colorblindMode.update((currentMode) =>
      currentMode === 'Normal' ? 'Protanopia' :
      currentMode === 'Protanopia' ? 'Deuteranopia' :
      'Normal'
    );
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

{#if showIcon}
  <button on:click={toggleColorblindMode} aria-label="Toggle Colorblind Mode">
    {#if $colorblindMode === 'Normal'}
      <EyeSolid color={$darkMode ? 'white' : 'black'} class="h-7 w-7 pointer-events-none" />
    {:else if $colorblindMode === 'Protanopia'}
      <EyeSolid color='#ff4c4c' class="h-7 w-7 pointer-events-none" />
    {:else if $colorblindMode === 'Deuteranopia'}
      <EyeSolid color='#4caf50' class="h-7 w-7 pointer-events-none" />
    {:else}
      <EyeSolid color="gray" class="h-7 w-7 pointer-events-none" /> <!-- Fallback icon to avoid disappearing -->
    {/if}
  </button>
{/if}
