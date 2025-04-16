<script lang="ts">
    export let likedImages: string[] = [];
    export let onSend: () => void;
    export let onReset: () => void;
    export let onReload: () => void;
    export let isSending: boolean = false;
  </script>
  
  <div class="liked-summary">
    <h3>Images likées ({likedImages.length})</h3>
    <div class="thumbnail-grid">
      {#each likedImages as image}
        <div class="thumbnail">
          <img src={`/images/${image}`} alt={image} />
          <span class="image-name">{image}</span>
        </div>
      {/each}
    </div>
    <div class="action-buttons">
      <button on:click={onSend} disabled={isSending}>
        {isSending ? 'Envoi...' : 'Envoyer les préférences'}
      </button>
      <button on:click={onReset}>Réinitialiser</button>
      <button on:click={onReload}>Charger de nouvelles images</button>
    </div>
  </div>
  
  <style>
    .liked-summary {
      margin-top: 20px;
    }
    
    .thumbnail-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 10px;
      margin: 20px 0;
    }
    
    .thumbnail {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    
    .thumbnail img {
      width: 100%;
      height: 100px;
      object-fit: cover;
      border-radius: 4px;
    }
    
    .image-name {
      font-size: 0.8rem;
      margin-top: 5px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      max-width: 100%;
    }
    
    .action-buttons {
      display: flex;
      gap: 10px;
      justify-content: center;
      margin-top: 10px;
    }
  </style>