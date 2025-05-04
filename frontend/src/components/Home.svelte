<!-- components/Home.svelte -->
<script lang="ts">
	import Card from './ui/Card.svelte';
	import Button from './ui/Button.svelte';
	import ImageViewer from './ImageViewer.svelte';
	import Message from './Message.svelte';

	import { imageStore } from '../stores/imageStore';
	import { onDestroy } from 'svelte';

	export let username: string;
	export let calibrated: boolean;

	let isCalibrating = false;

	let unsubscribe = imageStore.subscribe(() => {});
	onDestroy(unsubscribe);

	$: headerText = calibrated 
		? "Votre profil est calibré, vous pouvez continuer"
		: "Calibrez votre profil pour continuer";
	$: buttonText = calibrated ? "Reprendre" : "Calibrer";

	function startCalibration() {
		isCalibrating = true;
		imageStore.setUsername(username);
		imageStore.fetchImages();
	}

	const likeImage = () => imageStore.likeImage();
	const skipImage = () => imageStore.skipImage();

    async function handleSendPreferences() {
        await imageStore.sendPreferences();
        imageStore.resetSelection();
        isCalibrating = false;
        calibrated = true;
    }
</script>

<main class="main-content">
	{#if !isCalibrating}
		<Card>
			<h1>{headerText}</h1>
			<Button on:click={startCalibration} class="start-button">{buttonText}</Button>
		</Card>
	{:else}
		{#if $imageStore.isLoading}
			<p>Chargement des images...</p>
		{:else}
            {#if $imageStore.images.length > 0 && $imageStore.currentIndex < $imageStore.images.length}
                <ImageViewer
                    currentImage={$imageStore.images[$imageStore.currentIndex]}
                    currentIndex={$imageStore.currentIndex}
                    totalImages={$imageStore.images.length}
                    onLike={likeImage}
                    onSkip={skipImage}
                />
            {:else}
                <p>Vous avez parcouru toutes les images.</p>
                <Button 
                    on:click={handleSendPreferences} 
                    class="send-preferences-button"
                    disabled={$imageStore.isSending}>
                    { $imageStore.isSending ? "Envoi en cours..." : "Envoyer les préférences" }
                </Button>
            {/if}
    
			<Message message={$imageStore.resultMessage} />
		{/if}
	{/if}
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
        flex-direction: column;
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
