<script>
	export let label = '';
	export let type = 'text';
	export let value = '';
	export let placeholder = '';
	export let disabled = false;
</script>

<div class="input-field">
	{#if label}
		<label for={label.replace(/\s+/g, '')}>{label}</label>
	{/if}
	
	<input
		id={label.replace(/\s+/g, '')}
		{type}
		bind:value
		{placeholder}
		{disabled}
	/>
</div>

<style>
	.input-field {
		display: flex;
		flex-direction: column;
		margin-bottom: 1rem;
	}
	
	label {
		font-size: 0.9rem;
		margin-bottom: 0.5rem;
		color: #555;
		font-weight: 500;
	}
	
	input {
		padding: 0.75rem 1rem;
		border: 2px solid #e0e0e0;
		border-radius: 6px;
		font-size: 1rem;
		transition: border-color 0.2s, box-shadow 0.2s;
		outline: none;
	}
	
	input:focus {
		border-color: #6e8efb;
		box-shadow: 0 0 0 3px rgba(110, 142, 251, 0.2);
	}
	
	input:disabled {
		background-color: #f5f5f5;
		cursor: not-allowed;
	}
</style>