<!-- components/Home.svelte -->
<script lang="ts">
    import Card from './ui/Card.svelte';
    import Button from './ui/Button.svelte';
    import ImageViewer from './ImageViewer.svelte';
    import Message from './Message.svelte';
    import { authStore } from '../stores/authStore';
    import { imageStore } from '../stores/imageStore';
    import { onDestroy } from 'svelte';
    
    export let username: string;
    export let calibrated: boolean;
    let isCalibrating = false;
    
    $: { username = $authStore.username; calibrated = $authStore.calibrated; }
    
    let unsubscribe = imageStore.subscribe(() => {});
    onDestroy(unsubscribe);
    
    $: headerText = calibrated
        ? "Votre profil est calibré, vous pouvez continuer"
        : "Calibrez votre profil pour continuer";
    $: buttonText = calibrated ? "Reprendre" : "Calibrer";
    
    function startCalibration() {
        isCalibrating = true;
        imageStore.setUsername(username);
        imageStore.setCalibrated(calibrated);
        if (calibrated) {
            imageStore.fetchRecommendedImages();
        } else {
            imageStore.fetchCalibrationImages();
        }
    }
    
    const likeImage = () => imageStore.likeImage();
    const skipImage = () => imageStore.skipImage();
    
    async function handleSendPreferences() {
        await imageStore.sendPreferences();
        
        authStore.setCalibrated(true);
        
        imageStore.resetSelection();
        isCalibrating = false;
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
            <p class="loading-message">Réentrainement du modèle, chargement des nouvelles recommandations...</p>


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
           
                {#if !calibrated}
                    <Button
                        on:click={handleSendPreferences}
                        class="send-preferences-button"
                        disabled={$imageStore.isSending}>
                        { $imageStore.isSending ? "Envoi en cours..." : "Envoyer les préférences" }
                    </Button>
                {:else}
                    <Button
                        on:click={startCalibration}
                        class="restart-reco-button">
                        Relancer les recommandations
                    </Button>
                {/if}
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

    .loading-message {
    font-size: 2rem; 
    color: rgb(0, 0, 0);
    padding: 1rem 1rem;
    border-radius: 6px;
    text-align: center;
    margin: 1rem 0;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.85; }
    100% { transform: scale(1); opacity: 1; }
}
</style>
