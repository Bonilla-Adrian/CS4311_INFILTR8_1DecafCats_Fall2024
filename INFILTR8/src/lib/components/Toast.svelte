<script>
    import { notifications, markNotificationAsOld } from '$lib/stores/notifications.js'; // Remove 'removeNotification' as it's not needed
    import { Toast } from 'flowbite-svelte';
    import { fly, fade } from 'svelte/transition';
    import { BellRingSolid, CheckCircleSolid, ExclamationCircleSolid, InfoCircleSolid } from 'flowbite-svelte-icons';
    import { titleCase } from '$lib/utils.js';
    
    // Filter only new notifications
    $: notificationMessages = $notifications.filter(notification => notification.new);
  
    // Function to handle closing of notification (only mark as old now, no removal)
    function handleNotificationClose(id) {
      markNotificationAsOld(id); // Mark notification as old (to prevent it from showing up again in Toast)
    }
  
    // Icon determination based on notification type
    function getIcon(type) {
      switch (type) {
        case 'success':
          return CheckCircleSolid;
        case 'error':
          return ExclamationCircleSolid;
        case 'alert':
          return ExclamationCircleSolid;
        case 'message':
          return InfoCircleSolid;
        case 'notification':
          return BellRingSolid;
        default:
          return BellRingSolid;
      }
    }
  </script>
  
  <div class="fixed top-24 right-[10px] flex flex-col gap-1 z-[1050] max-h-[10px] min-w-[275px]">
    {#each notificationMessages as { id, message, type, timeout } (id)}
      <div 
        in:fade={{ duration: 800 }} 
        out:fade={{ duration: 800 }}
        on:introend={() => setTimeout(() => handleNotificationClose(id), timeout)} 
        on:outrostart={(e) => e.preventDefault()}
      >
        <Toast
          transition={fly}
          params={{ x: 200 }}
          color={type === 'success' ? 'green' : type === 'alert' ? 'red' : type === 'message' ? 'blue' : 'white'}
          divClass='w-full max-w-xs p-2 text-gray-500 bg-white shadow dark:text-gray-400 dark:bg-gray-800 gap-3 rounded-lg' 
          defaultIconClass='h-12 w-12'
          align={false}
          on:close={() => handleNotificationClose(id)}>
          <svelte:fragment slot="icon">
            {#if type}
              {#await getIcon(type) then Icon}
                <Icon class="h-10 w-10" />
              {/await}
            {/if}
          </svelte:fragment>
          <div class="font-semibold text-base text-gray-900 dark:text-white">{titleCase(type)}</div>
          <div class="text-base font-normal">{message}</div>
        </Toast>
      </div>
    {/each}
  </div>
  