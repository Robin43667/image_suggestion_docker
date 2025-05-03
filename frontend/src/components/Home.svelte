<!-- components/Home.svelte -->

<script>
	import Card from './ui/Card.svelte';
	import Button from './ui/Button.svelte';

	export let username;
	export let calibrated;

	function noop() {
		// Placeholder pour les boutons pas encore implémentés
	}

	// Texte conditionnel en fonction du profil calibré ou non
	$: headerText = calibrated 
		? "Votre profil est calibré, vous pouvez continuer"
		: "Calibrez votre profil pour continuer";

	$: buttonText = calibrated ? "Reprendre" : "Calibrer";
</script>

<main class="main-content">
	<Card>
		<h1>{headerText}</h1>
		<Button on:click={noop} class="start-button">{buttonText}</Button>
	</Card>        
</main>


<style>
    .main-content {
        flex-grow: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
        margin: 0 auto;
        max-width: 50%;
        height: 100%;
    }

    h1 {
        font-size: 1.75rem;
        color: #333;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .start-button {
        width: 100%;
        padding: 0.75rem 1rem;
        font-size: 1.1rem;
    }
</style>
