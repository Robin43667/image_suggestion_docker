<script>
	import { createEventDispatcher } from 'svelte';
	import { register } from '../lib/api';
	import { setAuthCookie } from '../lib/auth';
	import Button from './ui/Button.svelte';
	import Card from './ui/Card.svelte';
	import InputField from './ui/InputField.svelte';
	
	const dispatch = createEventDispatcher();
	
	let username = '';
	let password = '';
	let confirmPassword = '';
	let isLoading = false;
	let errorMessage = '';
	
	async function handleSubmit() {
		if (!username || !password || !confirmPassword) {
			errorMessage = 'Veuillez remplir tous les champs';
			return;
		}
		
		if (password !== confirmPassword) {
			errorMessage = 'Les mots de passe ne correspondent pas';
			return;
		}
		
		isLoading = true;
		errorMessage = '';
		
		try {
			const response = await register(username, password);
			
			if (response.status === 'success') {
				setAuthCookie(username);
				dispatch('authSuccess', { username });
			} else {
				errorMessage = response.message || 'Erreur lors de l\'inscription';
			}
		} catch (error) {
			errorMessage = 'Erreur de connexion au serveur';
			console.error(error);
		} finally {
			isLoading = false;
		}
	}
	
	function navigateToLogin() {
		dispatch('navigateToLogin');
	}
</script>

<Card>
	<div class="register-form">
		<h1>Inscription</h1>
		
		{#if errorMessage}
			<div class="error-message">{errorMessage}</div>
		{/if}
		
		<form on:submit|preventDefault={handleSubmit}>
			<InputField
				label="Nom d'utilisateur"
				type="text"
				bind:value={username}
				placeholder="Choisissez un nom d'utilisateur"
				disabled={isLoading}
			/>
			
			<InputField
				label="Mot de passe"
				type="password"
				bind:value={password}
				placeholder="Choisissez un mot de passe"
				disabled={isLoading}
			/>
			
			<InputField
				label="Confirmer le mot de passe"
				type="password"
				bind:value={confirmPassword}
				placeholder="Confirmez votre mot de passe"
				disabled={isLoading}
			/>
			
			<div class="form-actions">
				<Button type="submit" disabled={isLoading}>
					{isLoading ? 'Inscription en cours...' : 'S\'inscrire'}
				</Button>
			</div>
		</form>
		
		<div class="link-section">
			<p>Vous avez déjà un compte ?</p>
			<button class="link-button" on:click={navigateToLogin}>Se connecter</button>
		</div>
	</div>
</Card>

<style>
	.register-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}
	
	h1 {
		font-size: 1.8rem;
		color: #333;
		text-align: center;
		margin: 0;
		margin-bottom: 1rem;
	}
	
	.form-actions {
		margin-top: 1rem;
	}
	
	.error-message {
		padding: 0.75rem;
		background-color: #ffebee;
		color: #d32f2f;
		border-radius: 4px;
		font-size: 0.9rem;
	}
	
	.link-section {
		text-align: center;
		margin-top: 1rem;
	}
	
	.link-section p {
		margin: 0;
		color: #666;
		font-size: 0.9rem;
	}
	
	.link-button {
		background: none;
		border: none;
		color: #000000;
		cursor: pointer;
		font-weight: 500;
		padding: 0.5rem;
		font-size: 0.9rem;
		transition: color 0.2s;
	}
	
	.link-button:hover {
		color: #7300ff;
		text-decoration: underline;
	}
</style>