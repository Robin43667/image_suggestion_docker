<script lang="ts">
    import { onMount } from 'svelte';
    import type { EncodedImage } from '../stores/imageStore';
    import * as imageService from '../services/imageService';

    let images: EncodedImage[] = [];
    let isLoading = true;
    let errorMessage = '';

    onMount(async () => {
        try {
            const data = await imageService.fetchImages();
            if (data.images && data.images.length > 0) {
                images = data.images;
            } else {
                errorMessage = 'Aucune image disponible.';
            }
        } catch (error) {
            console.error('Erreur lors du chargement des images:', error);
            errorMessage = 'Erreur lors du chargement des images.';
        } finally {
            isLoading = false;
        }
    });
</script>

<style>
    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
        gap: 10px;
    }
    .preview {
        width: 80px;
        height: 80px;
        object-fit: cover;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
</style>

<main>
    <h1>Jeu de données d'images</h1>

    {#if isLoading}
        <p>Chargement des images...</p>
    {:else if errorMessage}
        <p>{errorMessage}</p>
    {:else}
        <div class="grid">
            {#each images as image}
                <img class="preview" src={`data:${image.mimeType};base64,${image.content}`} alt={image.filename} />
            {/each}
        </div>
    {/if}
</main>
