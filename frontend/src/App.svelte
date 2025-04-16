<!-- App.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { imageStore, type ImageStoreState } from './stores/imageStore';
  import ImageViewer from './components/ImageViewer.svelte';
  import LikedImages from './components/LikedImages.svelte';
  import LikedCount from './components/LikedCount.svelte';
  import Message from './components/Message.svelte';
  import DataActions from './components/DataActions.svelte'; 

  let storeValue: ImageStoreState;

  imageStore.subscribe(value => {
    storeValue = value;
  });

  onMount(() => {
    imageStore.fetchImages();
  });

  $: hasMoreImages = storeValue.currentIndex < storeValue.images.length;
  $: currentImage = hasMoreImages ? storeValue.images[storeValue.currentIndex] : null;
</script>

<section class="image-recommender">
  <h2>Recommendation d'Images</h2>

  <input
  type="text"
  placeholder="Entrez votre nom d'utilisateur"
  bind:value={storeValue.username}
  on:input={(e) => imageStore.setUsername((e.target as HTMLInputElement).value)}
  class="username-input"
/>


  <DataActions /> 

  {#if storeValue.isLoading}
    <p>Chargement des images...</p>
  {:else if !hasMoreImages}
    <div class="results">
      <p>Aucune image supplémentaire à afficher</p>
      {#if storeValue.likedImages.length > 0}
        <LikedImages 
          likedImages={storeValue.likedImages.map(img => img.filename)}
          onSend={imageStore.sendPreferences}
          onReset={imageStore.resetSelection}
          onReload={imageStore.fetchImages}
          isSending={storeValue.isSending}
        />
      {/if}
    </div>
  {:else}
    <ImageViewer 
      currentImage={currentImage}
      currentIndex={storeValue.currentIndex}
      totalImages={storeValue.images.length}
      onLike={imageStore.likeImage}
      onSkip={imageStore.skipImage}
    />
    
    {#if storeValue.likedImages.length > 0}
      <LikedCount 
        count={storeValue.likedImages.length}
        onSend={imageStore.sendPreferences}
        isSending={storeValue.isSending}
      />
    {/if}
  {/if}

  <Message message={storeValue.resultMessage} />
</section>

<style>
  .username-input {
    margin: 1rem 0;
    padding: 0.5rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    width: 100%;
    max-width: 300px;
  }
</style>
