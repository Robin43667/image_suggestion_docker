<!-- components/ui/Card.svelte -->

<div class="card">
	<slot></slot>
</div>

<style>
	.card {
		background-color: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
		width: 100%;
		box-sizing: border-box;
		transition: transform 0.3s, box-shadow 0.3s;
	}
	
	.card:hover {
		transform: translateY(-5px);
		box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
	}
</style>