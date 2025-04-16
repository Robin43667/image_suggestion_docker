<script lang="ts">
    export let message: string = '';
  </script>
  
  {#if message}
    <div class="message">{message}</div>
  {/if}
  
  <style>
    .message {
      margin-top: 20px;
      padding: 10px;
      background-color: #f0f0f0;
      border-radius: 4px;
      text-align: center;
    }
  </style>