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
        <button on:click={onLike} class="like-btn">Aimer</button>
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
      width: 100%;
      padding: 0.75rem 1.25rem;
      background: #ffffff;
      color: #000000;
      border: 2px solid #000000;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.2s, color 0.2s, transform 0.2s, box-shadow 0.2s;
      outline: none;
    }

    .like-btn:focus-visible {
      outline: 2px solid #000000;
      outline-offset: 2px;
    }

    .like-btn:hover:not(:disabled) {
      background-color: #00ff95;
      color: rgb(0, 0, 0);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .like-btn:active:not(:disabled) {
      transform: translateY(0);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }

    .like-btn:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }


    .skip-btn {
      width: 100%;
      padding: 0.75rem 1.25rem;
      background: #ffffff;
      color: #000000;
      border: 2px solid #000000;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.2s, color 0.2s, transform 0.2s, box-shadow 0.2s;
      outline: none;
    }

    .skip-btn:focus-visible {
      outline: 2px solid #000000;
      outline-offset: 2px;
    }

    .skip-btn:hover:not(:disabled) {
      background-color: #d80000;
      color: rgb(0, 0, 0);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .skip-btn:active:not(:disabled) {
      transform: translateY(0);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }

    .skip-btn:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
  </style>