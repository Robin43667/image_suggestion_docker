<!-- components/ui/Button.svelte -->

<script>
	export let type = 'button';
	export let disabled = false;
</script>

<button {type} {disabled} class="button" on:click>
	<slot></slot>
</button>

<style>
	.button {
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

	.button:focus-visible {
		outline: 2px solid #000000;
		outline-offset: 2px;
	}

	.button:hover:not(:disabled) {
		background-color: #000000;
		color: white;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
	}

	.button:active:not(:disabled) {
		transform: translateY(0);
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
	}

	.button:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}
</style>
