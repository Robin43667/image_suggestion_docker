<script lang="ts">
  import svelteLogo from './assets/svelte.svg'
  import viteLogo from '/vite.svg'
  import Counter from './lib/Counter.svelte'

  let isCollecting = false;
  let isAnalyzing = false;

  async function startCollection() {
    isCollecting = true;
    try {
      const response = await fetch("/start_collection");
      const result = await response.json();
      console.log("Réponse complète:", result);
      if (result.message) {
        alert(result.message);
      } else {
        alert("Réponse inattendue : " + JSON.stringify(result));
      }
    } catch (error) {
      console.error("Erreur lors du fetch :", error);
      alert("Erreur lors du démarrage de la collecte");
    }
    isCollecting = false;
  }

  async function startAnalysis() {
    isAnalyzing = true;
    try {
      const response = await fetch("/analyze");
      const result = await response.json();
      console.log("Résultat de l'analyse :", result);
      if (result.message) {
        alert(result.message);
      } else {
        alert("Réponse inattendue : " + JSON.stringify(result));
      }
    } catch (error) {
      console.error("Erreur lors de l'analyse :", error);
      alert("Erreur lors du lancement de l'analyse");
    }
    isAnalyzing = false;
  }
</script>

<main>
  <section class="collect">
    <h2>Collecte des données</h2>
    <button on:click={startCollection} disabled={isCollecting}>
      {isCollecting ? "Collecte en cours..." : "Démarrer la collecte"}
    </button>
    <br /><br />
    <button on:click={startAnalysis} disabled={isAnalyzing}>
      {isAnalyzing ? "Analyse en cours..." : "Lancer l'analyse"}
    </button>
  </section>
</main>

<style>
  .collect {
    margin-top: 2rem;
    text-align: center;
  }

  button {
    background-color: #646cff;
    border: none;
    padding: 0.8em 1.5em;
    font-size: 1rem;
    color: white;
    border-radius: 0.5em;
    cursor: pointer;
    transition: background 0.3s;
  }

  button:disabled {
    background-color: #888;
    cursor: not-allowed;
  }

  button:hover:not(:disabled) {
    background-color: #4e52d1;
  }

  button + button {
    margin-top: 1rem;
  }
</style>
