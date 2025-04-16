<script lang="ts">
    export let currentImage: { filename: string, content: string, mimeType: string } | null;
    export let currentIndex: number;
    export let totalImages: number;
    export let onLike: () => void;
    export let onSkip: () => void;
  </script>
  
  {#if currentImage}
    <div class="image-container">
      <img
        src={`data:${currentImage.mimeType};base64,${currentImage.content}`}
        alt={currentImage.filename}
      />
      <div class="image-info">
        <span class="image-name">{currentImage.filename}</span>
        <span class="counter">{currentIndex + 1}/{totalImages}</span>
      </div>
      <div class="action-buttons">
        <button on:click={onLike} class="like-btn">J'aime</button>
        <button on:click={onSkip} class="skip-btn">Passer</button>
      </div>
    </div>
  {/if}
  
  
  
  <style>
    .image-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 20px;
    }
    
    .image-container img {
      max-width: 100%;
      max-height: 500px;
      object-fit: contain;
      border-radius: 8px;
      margin-bottom: 10px;
    }
    
    .image-info {
      display: flex;
      justify-content: space-between;
      width: 100%;
      margin-bottom: 10px;
    }
    
    .action-buttons {
      display: flex;
      gap: 10px;
      justify-content: center;
      margin-top: 10px;
    }
    
    .like-btn {
      background-color: #4CAF50;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    
    .skip-btn {
      background-color: #f44336;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
  </style>