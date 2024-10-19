<script>
    import { SunSolid, MoonSolid } from 'flowbite-svelte-icons';
    import { onMount } from 'svelte';
  
  
    let darkMode = false;
  
  
    onMount(() => {
      if (localStorage.getItem('color-theme') === 'dark') {
        darkMode = true;
        document.cookie = 'color-theme=dark; max-age=31536000; path=/';
        document.documentElement.classList.add('dark');
        
      }
      else {
        darkMode = false;
        document.cookie = 'color-theme=light; max-age=31536000; path=/';
      }
    });
  
  
    let toggleDarkMode = () => {
      if (darkMode) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('color-theme', 'light');
        // Set a cookie for dark-mode as well as localStorage
        document.cookie = 'color-theme=light; max-age=31536000; path=/';
        darkMode = false;
      }
      else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('color-theme', 'dark');
        // Set a cookie for dark-mode as well as localStorage
        document.cookie = 'color-theme=dark; max-age=31536000; path=/';
        darkMode = true;
      }
    }
  </script>
  
  <button on:click={toggleDarkMode}>
    {#if darkMode}
    <SunSolid color='white' class="pointer-events-none" />
    {:else}
    <MoonSolid class="pointer-events-none" />
    {/if}
  </button>