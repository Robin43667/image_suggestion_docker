<!-- components/Login.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { login } from '../lib/api';
    import { authStore } from '../stores/authStore';
    import Button from './ui/Button.svelte';
    import Card from './ui/Card.svelte';
    import InputField from './ui/InputField.svelte';
   
    const dispatch = createEventDispatcher();
    let username = '';
    let password = '';
    let isLoading = false;
    let errorMessage = '';
   
	async function handleSubmit() {
		if (!username || !password) {
			errorMessage = 'Veuillez remplir tous les champs';
			return;
		}
	
		isLoading = true;
		errorMessage = '';
	
		try {
			const response = await login(username, password);
	
			if (response.status === 'success' && response.user) {
				authStore.login(response.user.username, response.user.calibrated);
	
				dispatch('authSuccess', {
					username: response.user.username,
					calibrated: response.user.calibrated
				});
			} else {
				errorMessage = response.message || 'Identifiants incorrects';
			}
		} catch (error) {
			console.error('Erreur de connexion:', error);
			errorMessage = 'Erreur de connexion au serveur';
		} finally {
			isLoading = false;
		}
	}
	
   
    function navigateToRegister() {
        dispatch('navigateToRegister');
    }
</script>
<Card>
    <div class="login-form">
        <h1>Connexion</h1>
        {#if errorMessage}
            <div class="error-message">{errorMessage}</div>
        {/if}
        <form on:submit|preventDefault={handleSubmit}>
            <InputField
                label="Nom d'utilisateur"
                type="text"
                bind:value={username}
                placeholder="Entrez votre nom d'utilisateur"
                disabled={isLoading}
            />
            <InputField
                label="Mot de passe"
                type="password"
                bind:value={password}
                placeholder="Entrez votre mot de passe"
                disabled={isLoading}
            />
            <div class="form-actions">
                <Button type="submit" disabled={isLoading}>
                    {isLoading ? 'Connexion en cours...' : 'Se connecter'}
                </Button>
            </div>
        </form>
        <div class="link-section">
            <p>Vous n'avez pas de compte ?</p>
            <button class="link-button" on:click={navigateToRegister}>Créer un compte</button>
        </div>
    </div>
</Card>

<style>
	.login-form {
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