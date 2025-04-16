<script lang="ts">
    export let count: number;
    export let onSend: () => void;
    export let isSending: boolean = false;
  </script>
  
  <div class="liked-count">
    <span>Images likées: {count}</span>
    <button on:click={onSend} disabled={isSending} class="send-btn">
      {isSending ? 'Envoi...' : 'Envoyer les préférences'}
    </button>
  </div>
  
  <style>
    .liked-count {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 20px;
      padding: 10px;
      background-color: #f0f0f0;
      border-radius: 4px;
    }
    
    .send-btn {
      background-color: #2196F3;
      color: white;
      padding: 8px 16px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
  </style>