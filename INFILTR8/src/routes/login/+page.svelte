<script>
  import { onMount } from 'svelte';
  import { Card, Modal } from 'flowbite-svelte';
  import { goto } from '$app/navigation';
  import { session, checkSession } from '$lib/stores/session';

  let username = '';
  let password = '';
  let errorMessage = '';

  let showCreateAccountModal = false;
  let showForgotPasswordModal = false;

  // Reactive variable to control autocomplete
  let autocomplete = 'on';

  onMount(() => {
    checkSession(); // Check session on page load
  });

  // Disable autocomplete when modals are opened by changing the reactive variable
  function handleModalOpen(modalType) {
    if (modalType === 'createAccount') {
      showCreateAccountModal = true;
    } else if (modalType === 'forgotPassword') {
      showForgotPasswordModal = true;
    }

    // Disable autocomplete while modals are open
    autocomplete = 'off';
  }

  // Re-enable autocomplete when modals are closed
  function handleModalClose() {
    showCreateAccountModal = false;
    showForgotPasswordModal = false;
    autocomplete = 'on';
  }

  async function loginUser() {
    const response = await fetch('/flask-api/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'}, 
      body: JSON.stringify({ username, password })
    });

    if (response.ok) {
      const result = await response.json();
      console.log(result.status); // "Login successful"
      await checkSession(); // Update session store
      goto('/dashboard');
    } else {
      console.error('Failed to login');
    }
  }
</script>

<div class="flex items-center justify-center min-h-screen">
  <form on:submit|preventDefault={loginUser} class="w-full max-w-md">
    <Card size='lg'>
      <h2 class="text-xl font-bold mb-3">Login</h2>
      {#if errorMessage}
        <div class="text-red-600 dark:text-red-400">{errorMessage}</div>
      {/if}

      <div class="relative z-0 w-full mb-6 group">
        <!-- Use shorthand for reactive autocomplete -->
        <input type="text" id="username" bind:value={username} placeholder=" " required
          {autocomplete} class="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer" />
        <label for="username" class="absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-6 scale-75 top-3 -z-10 origin-[0] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6">Username</label>
      </div>

      <div class="relative z-0 w-full mb-6 group">
        <!-- Use shorthand for reactive autocomplete -->
        <input type="password" id="password" bind:value={password} placeholder=" " required
          {autocomplete} class="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer" />
        <label for="password" class="absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-6 scale-75 top-3 -z-10 origin-[0] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6">Password</label>
      </div>

      <button type="submit" class="w-full py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-500 dark:hover:bg-blue-600 dark:focus:ring-blue-700">
        Login
      </button>

      <div class="mt-4 text-sm text-center text-gray-500 dark:text-gray-400">
        <button type="button" class="cursor-pointer hover:underline" on:click={() => handleModalOpen('createAccount')}>Create Account</button>
        &nbsp;|&nbsp;
        <button class="cursor-pointer hover:underline" on:click={() => handleModalOpen('forgotPassword')}>Forgot Password</button>
      </div>
    </Card>
  </form>

  <!-- Create Account Modal -->
  <Modal open={showCreateAccountModal} on:close={handleModalClose}>
    <div class="p-4">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white">Create Account</h3>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Enter your details to create a new account.</p>
      <div class="mt-4">
        <button class="w-full px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-500 dark:hover:bg-blue-600 dark:focus:ring-blue-700"
          on:click={handleModalClose}>Close</button>
      </div>
    </div>
  </Modal>

  <!-- Forgot Password Modal -->
  <Modal open={showForgotPasswordModal} on:close={handleModalClose}>
    <div class="p-4">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white">Forgot Password</h3>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Enter your email to reset your password.</p>
      <input type="email" id="forgot-password-email" placeholder="Enter your email" class="w-full p-2 mt-4 bg-gray-100 dark:bg-gray-700 rounded-md"/>
      <div class="mt-4">
        <button class="w-full px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-500 dark:hover:bg-blue-600 dark:focus:ring-blue-700"
          on:click={handleModalClose}>Close</button>
      </div>
    </div>
  </Modal>
</div>
