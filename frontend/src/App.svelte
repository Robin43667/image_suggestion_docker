<!-- App.svelte -->

<script lang="ts">
	import { onMount } from 'svelte';
	import Login from './components/Login.svelte';
	import Register from './components/Register.svelte';
	import Home from './components/Home.svelte';
	import Button from './components/ui/Button.svelte';
	import { checkAuthentication } from './lib/auth';

	let currentRoute = 'login';
	let isAuthenticated = false;
	let username = '';
	let calibrated = false;

	onMount(async () => {
		const authResult = await checkAuthentication();
		isAuthenticated = authResult.isAuthenticated;
		username = authResult.username;
		calibrated = authResult.calibrated;

		if (isAuthenticated) {
			currentRoute = 'home';
		}
	});

	function handleAuthSuccess(event) {
		isAuthenticated = true;
		username = event.detail.username;
		calibrated = event.detail.calibrated;
		currentRoute = 'home';
	}

	function navigateTo(route) {
		currentRoute = route;
	}

	function handleLogout() {
		isAuthenticated = false;
		username = '';
		currentRoute = 'login';
		document.cookie = "auth=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
	}

	function goToProfile() {
		console.log('Redirection vers le profil');
	}

	$: userInitial = username ? username.charAt(0).toUpperCase() : '';
</script>
<main>
  {#if isAuthenticated}
  <header class="menu">
    <nav class="nav-actions">
      <button class="avatar-button" on:click={goToProfile} title="Profil">
        <span class="avatar-letter">{userInitial}</span>
      </button>
      <Button on:click={() => navigateTo('home')}>Profil</Button>
      <Button on:click={() => console.log('Documentation')}>Documentation</Button>
      <Button on:click={() => console.log('API')}>API</Button>
      <Button on:click={() => console.log('Dataset')}>Dataset</Button>
      <Button on:click={() => console.log('Tasks')}>Tasks</Button>
      <button class="avatar-button logout-button" on:click={handleLogout} title="Déconnexion">
        <svg class="logout-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </nav>
  </header>
{/if}

	<div class="page-content">
		{#if currentRoute === 'login'}
			<div class="container narrow">
				<Login 
					on:navigateToRegister={() => navigateTo('register')} 
					on:authSuccess={handleAuthSuccess}
				/>
			</div>
		{:else if currentRoute === 'register'}
			<div class="container narrow">
				<Register 
					on:navigateToLogin={() => navigateTo('login')} 
					on:authSuccess={handleAuthSuccess}
				/>
			</div>
		{:else if currentRoute === 'home'}
			<div class="container">
				<Home {username} {calibrated} />
			</div>
		{/if}
	</div>

	<footer class="footer">
		© Ribadou Corp
	</footer>
</main>


<style>
  main {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: linear-gradient(135deg, #3F5EFB, #ff0033);
    font-family: 'Roboto', sans-serif;
  }

  .page-content {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
  }

  .container {
    width: 80%;
    margin: 0 auto;
    flex-grow: 1;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .container.narrow {
    max-width: 400px;
  }

	.menu {
		display: flex;
		justify-content: center;
		padding: 1.5rem;
	}

	.nav-actions {
		display: flex;
		gap: 0.5rem;
		align-items: center;
	}

	.avatar-button {
		width: 40px;
		height: 40px;
		border-radius: 50%;
		background-color: #ffffff;
		aspect-ratio: 1;
		color: #000000;
		font-weight: bold;
		font-size: 1rem;
		border: 2px solid #000000;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: background-color 0.2s, color 0.2s, transform 0.2s;
	}

	.avatar-button:hover {
		background-color: #000000;
		color: #ffffff;
		transform: translateY(-2px);
	}

	.avatar-letter {
		display: block;
		line-height: 1;
	}

	.logout-icon {
		width: 20px;
		height: 20px;
	}
  
  .footer {
    text-align: center;
    padding: 0.5rem;
    font-size: 0.85rem;
    color: #000000;
  }
</style>
