<script>
  import { ThumbsUpSolid, ThumbsDownSolid } from 'flowbite-svelte-icons';
  import { Card } from 'flowbite-svelte';
  import { goto } from '$app/navigation'
  import { session, checkSession } from '../../lib/stores/session';
  import { onMount } from 'svelte';

  onMount(() => {
    checkSession(); // Check session on page load
  });
 
  let username = '';
  let password = '';
  let errorMessage = '';

  async function loginUser() {
    const response = await fetch('/flask-api/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ username, password })});

    if (response.ok) {
      const result = await response.json();
      console.log(result.status); // "Login successful"
      await checkSession(); // Update session store
      goto('/dashboard')
    } else {
      console.error('Failed to login');
    }
  }

  let selectedScheme = 'Default';  // Default scheme
  let colorSchemes = {
    'Default': {
      bg: 'bg-white dark:bg-gray-900', text: 'text-black dark:text-white', primary: 'bg-blue-500', danger: 'bg-red-500', success: 'bg-green-500', warning: 'bg-yellow-500',
    }
  };
  $: currentScheme = colorSchemes[selectedScheme];
  

</script>


<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
  }

  .login-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    text-align: center;
    background: var(--background-color);
    transition: background 0.3s ease;
    position: relative;
  }

  .login-form {
    background-color: var(--background-color);
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    width: 350px;
  }

  h1.brand {
    margin-bottom: 20px;
    font-size: 36px;
    color: var(--brand-color);
  }

  h2 {
    margin-bottom: 20px;
    font-size: 24px;
  }

  .form-group {
    margin-bottom: 15px;
  }

  .form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: var(--label-color);
  }

  .form-group input {
    width: 100%;
    padding: 10px;
    font-size: 16px;
    border: 1px solid var(--input-border);
    border-radius: 4px;
    background: var(--input-background);
    color: var(--input-text);
  }

  .form-group input:focus {
    border-color: var(--input-focus-border);
    outline: none;
  }

  .error-message {
    color: var(--error-color);
    margin-bottom: 15px;
  }

  .submit-button {
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    background-color: var(--button-background);
    color: var(--button-text);
    border: none;
    border-radius: 4px;
    transition: background-color 0.3s ease;
  }

  .submit-button:hover {
    text-decoration: underline;
  }

  .forgot-password {
    display: block;
    margin-top: 15px;
    font-size: 14px;
    color: var(--forgot-password-color);
    text-decoration: none;
  }

  .forgot-password:hover {
    text-decoration: underline;
  }
</style>

<div class={`login-container ${currentScheme.bg} ${currentScheme.text}`}>
  <h1 class="brand">INFILTR8</h1>
  
<form on:submit|preventDefault={loginUser}>
  <div class="login-form">
        <h2>Login</h2>
        {#if errorMessage}
      <div class="error-message">{errorMessage}</div>
      {/if}
      <div class="form-group"> 
          <label for="username" class="text-left">Username</label>
          <input type="text" id="username" bind:value={username} placeholder="Enter your username" />
      </div>
      <div class="form-group">
          <label for="password" class="text-left">Password</label>
          <input type="password" id="password" bind:value={password} placeholder="Enter your password" />
      </div>
      <a href="/forgot-password" class="forgot-password">Forgot password?</a>
      <button type="submit">Login</button>
    </div>
</form>
</div>

