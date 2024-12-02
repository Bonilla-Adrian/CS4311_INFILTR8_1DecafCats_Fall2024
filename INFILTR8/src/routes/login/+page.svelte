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

	// Create Account Form Variables
	let createUsername = '';
	let createPassword = '';
	let createErrorMessage = '';
	let createSuccessMessage = '';
	let recoveryKey = ''; // Store the recovery key to display

	// Forgot Password Form Variables
	let accountKey = '';
	let forgotUsername = '';
	let keyProvided = true; // Assume user has the account key initially
	let keyVerified = false; // Flag to show password reset form
	let recoveryKeyError = '';
	let passwordResetMessage = '';
	let adminResetMessage = '';

	// Reactive variable to control autocomplete
	let autocomplete = 'on';

	let showRequestAcceptedModal = false; // Modal state for checking request status
	let checkUsername = ''; // Username to check request status
	let requestStatusMessage = '';
	let showResetPasswordForm = false; // New variable to control form visibility
	let newPassword = '';

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

	// Re-enable autocomplete when modals are closed and reset modal states
	function handleModalClose() {
		showCreateAccountModal = false;
		showForgotPasswordModal = false;

		// Reset Create Account modal state
		createUsername = '';
		createPassword = '';
		createErrorMessage = '';
		createSuccessMessage = '';
		recoveryKey = '';

		// Reset Forgot Password modal state
		keyProvided = true; // Default to assuming the user has the account key
		accountKey = '';
		newPassword = '';
		forgotUsername = '';
		checkUsername = ''; // Reset username for status check
		keyVerified = false;
		recoveryKeyError = '';
		passwordResetMessage = '';
		adminResetMessage = '';
		requestStatusMessage = '';
		showRequestAcceptedModal = false; // Ensure "Check Status" state is reset
		showResetPasswordForm = false; // Ensure password reset form visibility is reset

		// Reset autocomplete to default
		autocomplete = 'on';
	}

	async function submitNewPassword() {
		if (!newPassword || !accountKey) {
			alert('Please enter your recovery key and a new password.');
			return;
		}

		try {
			const response = await fetch('/flask-api/reset-password', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ recovery_key: accountKey, new_password: newPassword })
			});

			const data = await response.json();

			if (response.ok) {
				alert('Password reset successfully. You may now log in with your new password.');
				passwordResetMessage = 'Password reset successful!';
				handleModalClose();
			} else {
				alert(data.error || 'Failed to reset password. Please try again.');
			}
		} catch (error) {
			console.error('Error in submitNewPassword:', error);
			alert('An error occurred while resetting the password.');
		}
	}

	// Function to check the status of the password reset request
	async function checkRequestStatus() {
		if (!checkUsername) {
			alert('Please enter your username.');
			return;
		}

		try {
			const response = await fetch('/flask-api/password-reset-status', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: checkUsername })
			});

			if (response.ok) {
				const data = await response.json();
				requestStatusMessage = `Your request status: ${data.status}`;
				showResetPasswordForm = data.status === 'approved'; // Show reset form if status is approved
			} else {
				const error = await response.json();
				requestStatusMessage = error.error || 'Failed to check request status.';
				showResetPasswordForm = false;
			}
		} catch (error) {
			console.error('Error in checkRequestStatus:', error);
			alert('An error occurred while checking the password reset request status.');
		}
	}

	async function loginUser() {
		const response = await fetch('/flask-api/login', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ username, password })
		});

		if (response.ok) {
			const result = await response.json();
			console.log(result.status); // should be admin or user
			await checkSession(); // Update session store
			goto('/dashboard');
		} else {
			errorMessage = 'Failed to login';
		}
	}
	

	async function createUser() {
		createErrorMessage = '';
		createSuccessMessage = '';
		recoveryKey = ''; // Reset recovery key each time the form is submitted

		const payload = {
			username: createUsername,
			password: createPassword
		};

		try {
			const response = await fetch('/flask-api/create_user', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});

			const data = await response.json();

			if (response.status === 201) {
				createSuccessMessage = 'User created successfully!';
				recoveryKey = data.recovery_key; // Capture the recovery key
				createUsername = '';
				createPassword = '';
			} else if (response.status === 409) {
				createErrorMessage = data.error || 'Error: Username already exists';
			} else {
				createErrorMessage = data.error || 'Failed to create user';
			}
		} catch (error) {
			createErrorMessage = 'An error occurred: ' + error.message;
		}
	}

	async function submitForgotPassword() {
		if (!forgotUsername) {
			alert('Please enter your username.');
			return;
		}

		try {
			const response = await fetch('/flask-api/request-password-reset', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: forgotUsername }) // Send username to backend
			});

			if (response.ok) {
				const data = await response.json();
				console.log('Password reset request sent:', data);
				alert('Your password reset request has been sent to the admin.');
			} else {
				const error = await response.json();
				console.error('Error requesting password reset:', error);
				alert('Failed to send password reset request. Please try again.');
			}
		} catch (error) {
			console.error('Error submitting password reset request:', error);
			alert('An error occurred while sending the password reset request.');
		} finally {
			handleModalClose(); // Close the modal after submission
		}
	}

	async function verifyRecoveryKey() {
		recoveryKeyError = '';
		passwordResetMessage = '';

		const response = await fetch('/flask-api/verify_recovery_key', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ recovery_key: accountKey })
		});

		const data = await response.json();

		if (response.ok) {
			keyVerified = true;
			passwordResetMessage = 'Recovery key verified! Enter your new password below.';
		} else {
			recoveryKeyError = data.error || 'Invalid recovery key';
		}
	}

	async function resetPassword() {
		passwordResetMessage = '';
		recoveryKeyError = '';

		const response = await fetch('/flask-api/reset-password', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ recovery_key: accountKey, new_password: newPassword })
		});

		const data = await response.json();

		if (response.ok) {
			passwordResetMessage =
				'Password reset successful! You can now log in with your new password.';
			keyVerified = false;
			accountKey = '';
			newPassword = '';
		} else {
			recoveryKeyError = data.error || 'Failed to reset password';
		}
	}


	async function requestAdminReset() {
		adminResetMessage = ''; // Reset the admin reset message

		if (!forgotUsername) {
			adminResetMessage = 'Please enter a valid username for the admin reset request.';
			return;
		}

		try {
			const response = await fetch('/flask-api/request-password-reset', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: forgotUsername })
			});

			if (response.ok) {
				const data = await response.json();
				adminResetMessage = `Admin reset request sent for ${forgotUsername}. Please contact support for further assistance.`;
				console.log('Admin reset request successful:', data);
			} else {
				const error = await response.json();
				adminResetMessage =
					error.message || 'Failed to send admin reset request. Please try again.';
				console.error('Admin reset request failed:', error);
			}
		} catch (error) {
			console.error('Error in requestAdminReset:', error);
			adminResetMessage =
				'An error occurred while processing your request. Please try again later.';
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center">
	<form on:submit|preventDefault={loginUser} class="w-full max-w-md">
		<Card size="lg">
			<h2 class="mb-4 text-xl font-bold">Login</h2>
			{#if errorMessage}
				<div class="-mt-4 mb-3 text-red-600 dark:text-red-400">{errorMessage}</div>
			{/if}

			<div class="group relative z-0 mb-6 w-full">
				<input
					type="text"
					id="username"
					bind:value={username}
					placeholder=" "
					required
					{autocomplete}
					class="peer block w-full appearance-none border-0 border-b-2 border-gray-300 bg-transparent px-0 py-2.5 text-sm text-gray-900 focus:border-blue-600 focus:outline-none focus:ring-0 dark:border-gray-600 dark:text-white dark:focus:border-blue-500"
				/>
				<label
					for="username"
					class="absolute top-3 -z-10 origin-[0] -translate-y-7 scale-75 transform text-sm text-gray-500 duration-300 peer-placeholder-shown:translate-y-0 peer-placeholder-shown:scale-100 peer-focus:-translate-y-7 peer-focus:scale-75 dark:text-gray-400"
					>Username</label
				>
			</div>

			<div class="group relative z-0 mb-6 w-full">
				<input
					type="password"
					id="password"
					bind:value={password}
					placeholder=" "
					required
					{autocomplete}
					class="peer block w-full appearance-none border-0 border-b-2 border-gray-300 bg-transparent px-0 py-2.5 text-sm text-gray-900 focus:border-blue-600 focus:outline-none focus:ring-0 dark:border-gray-600 dark:text-white dark:focus:border-blue-500"
				/>
				<label
					for="password"
					class="absolute top-3 -z-10 origin-[0] -translate-y-7 scale-75 transform text-sm text-gray-500 duration-300 peer-placeholder-shown:translate-y-0 peer-placeholder-shown:scale-100 peer-focus:-translate-y-7 peer-focus:scale-75 dark:text-gray-400"
					>Password</label
				>
			</div>

			<button
				type="submit"
				class="w-full rounded-lg bg-blue-600 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 dark:bg-blue-500 dark:hover:bg-blue-600 dark:focus:ring-blue-700"
				>Login</button
			>

			<div class="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
				<a href="/" class="cursor-pointer hover:underline">Home</a>
				&nbsp;|&nbsp;
				<button
					type="button"
					class="cursor-pointer hover:underline"
					on:click={() => handleModalOpen('createAccount')}>Create Account</button
				>
				&nbsp;|&nbsp;
				<button
					class="cursor-pointer hover:underline"
					on:click={() => handleModalOpen('forgotPassword')}>Forgot Password</button
				>
			</div>
		</Card>
	</form>

	<!-- Create Account Modal -->
	<Modal open={showCreateAccountModal} on:close={handleModalClose}>
		<div class="p-4">
			<h3 class="text-xl font-semibold text-gray-900 dark:text-white">Create Account</h3>
			<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
				Enter your details to create a new account.
			</p>

			{#if createErrorMessage}
				<div class="mb-2 mt-2 text-red-600 dark:text-red-400">{createErrorMessage}</div>
			{/if}
			{#if createSuccessMessage}
				<div class="mt-2 text-green-600 dark:text-green-400">{createSuccessMessage}</div>
			{/if}

			<form on:submit|preventDefault={createUser} class="mt-4 space-y-4">
				<input
					type="text"
					id="create-username"
					bind:value={createUsername}
					placeholder="Username"
					required
					class="w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
				/>
				<input
					type="password"
					id="create-password"
					bind:value={createPassword}
					placeholder="Password"
					required
					class="w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
				/>
				<button
					type="submit"
					class="w-full rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 dark:bg-blue-500 dark:hover:bg-blue-600 dark:focus:ring-blue-700"
					>Create Account</button
				>
			</form>

			{#if recoveryKey}
				<div class="mt-4 rounded-lg bg-yellow-100 p-4 dark:bg-yellow-700">
					<h4 class="font-semibold text-yellow-800 dark:text-yellow-300">
						Important: Save Your Recovery Key
					</h4>
					<p class="mt-2 text-sm text-gray-700 dark:text-gray-200">
						This key is required to reset your password if needed. Please store it in a secure
						location.
					</p>
					<div
						class="mt-2 rounded-md bg-gray-50 p-2 font-mono text-lg text-gray-900 dark:bg-gray-800 dark:text-white"
					>
						{recoveryKey}
					</div>
				</div>
			{/if}
		</div>
	</Modal>

	<!-- Forgot Password Modal -->
	<!-- Forgot Password Modal -->
	<Modal open={showForgotPasswordModal} on:close={handleModalClose}>
		<div class="p-4">
			<!-- Title and Instructions -->
			{#if !keyProvided && !keyVerified && !showRequestAcceptedModal}
				<h3 class="text-xl font-semibold text-gray-900 dark:text-white">Request Admin Reset</h3>
				<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
					Enter your username and admins credentials to request a reset or check your request status.
				</p>
				
			{:else if showRequestAcceptedModal}
				<h3 class="text-xl font-semibold text-gray-900 dark:text-white">Check Status</h3>
				<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
					Enter your username to check the status of your password reset request.
				</p>
			{:else if keyProvided && !keyVerified}
				<h3 class="text-xl font-semibold text-gray-900 dark:text-white">
					Reset Password with Recovery Key
				</h3>
				<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
					Enter your username and recovery key to reset your password.
				</p>
			{:else}
				<h3 class="text-xl font-semibold text-gray-900 dark:text-white">Reset Your Password</h3>
				<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Enter your new password below.</p>
			{/if}

			<!-- Error and Success Messages -->
			{#if recoveryKeyError}
				<div class="mt-2 text-red-600 dark:text-red-400">{recoveryKeyError}</div>
			{/if}
			{#if passwordResetMessage}
				<div class="mt-2 text-green-600 dark:text-green-400">{passwordResetMessage}</div>
			{/if}
			{#if adminResetMessage}
				<div class="mt-2 text-blue-600 dark:text-blue-400">{adminResetMessage}</div>
			{/if}
			{#if requestStatusMessage}
				<!-- Adjusted the location and styling of the status message -->
				<div class="mt-2 text-green-600 dark:text-green-400">{requestStatusMessage}</div>
			{/if}

			<!-- Modal Content -->
			{#if keyProvided && !keyVerified}
				<!-- Recovery Key Input  Sebastian changes-->
				<input
					type="text"
					id="account-username"  
					bind:value={username}  
					placeholder="Enter your Username"
					class="mt-4 w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
				/>
				<input
					type="text"
					id="account-key"
					bind:value={accountKey}
					placeholder="Enter your account key"
					class="mt-4 w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
				/>
				<button
					on:click={verifyRecoveryKey}
					class="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2 text-white"
				>
					Verify Recovery Key
				</button>
			{:else if !keyProvided && !showRequestAcceptedModal}
				<!-- Username Input for Admin Reset -->
				<input
					type="text"
					id="forgot-username"
					bind:value={forgotUsername}
					placeholder="Enter your username"
					class="mt-4 w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
				/>
				<!-- Sebastian Code -->
				<input
					type="text"
					id="forgot-username"
					bind:value={username}
					placeholder="Enter Admin Username "
					class="mt-4 w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
				/>
				<!--Sebastian Code -->
				<input
					type="text"
					id="forgot-username"
					bind:value={password}
					placeholder="Enter Admin Password"
					class="mt-4 w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
				/>
				<button
					on:click={requestAdminReset && }
					class="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2 text-white"
				>
					Reset Password 
				</button>

				<!-- Toggle to Check Status -->
				<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
					<button
						class="cursor-pointer text-indigo-600 hover:underline"
						on:click={() => {
							showRequestAcceptedModal = true;
							adminResetMessage = '';
						}}
					>
						Check Status of Your Request
					</button>
				</p>
			{:else if showRequestAcceptedModal}
				<!-- Check Status Input -->
				<input
					type="text"
					id="check-username"
					bind:value={checkUsername}
					placeholder="Enter your username"
					class="mt-4 w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
					disabled={showResetPasswordForm}
				/>
				{#if !showResetPasswordForm}
					<button
						on:click={checkRequestStatus}
						class="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2 text-white"
					>
						Check Status
					</button>
				{/if}

				<!-- Password Reset Form if Status is Approved -->
				{#if showResetPasswordForm}
					<input
						type="password"
						id="new-password"
						bind:value={newPassword}
						placeholder="Enter your new password"
						class="mt-4 w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
					/>
					<button
						on:click={resetPassword}
						class="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2 text-white"
					>
						Reset Password
					</button>
				{/if}

				<!-- Back to Admin Reset -->
				<div class="mt-4">
					<button
						class="cursor-pointer text-indigo-600 hover:underline"
						on:click={() => {
							showRequestAcceptedModal = false;
							showResetPasswordForm = false; // Reset password form visibility
							requestStatusMessage = ''; // Reset status message
						}}
					>
						Go Back to Admin Reset
					</button>
				</div>
			{:else}
				<!-- Password Reset Form -->
				<input
					type="password"
					id="new-password"
					bind:value={newPassword}
					placeholder="Enter your new password"
					class="mt-4 w-full rounded-md bg-gray-100 p-2 dark:bg-gray-700"
				/>
				<button
					on:click={resetPassword}
					class="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2 text-white"
				>
					Reset Password
				</button>
			{/if}

			<!-- Lost Account Key -->
			<div class="mt-4">
				{#if keyProvided}
					<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
						Lost your account key?
						<button
							class="cursor-pointer text-indigo-600 hover:underline"
							on:click={() => (keyProvided = false)}
						>
							Click here
						</button>
					</p>
				{/if}
			</div>
		</div>
	</Modal>
</div>
