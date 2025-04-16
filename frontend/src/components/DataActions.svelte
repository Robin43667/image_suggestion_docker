<script lang="ts">
    let isCollecting = false;
    let isAnalyzing = false;
    let isRecommending = false;
  
    async function startCollection() {
      isCollecting = true;
      try {
        const response = await fetch("/start_collection");
        const result = await response.json();
        console.log("Réponse complète:", result);
        alert(result.message ?? "Réponse inattendue : " + JSON.stringify(result));
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
        alert(result.message ?? "Réponse inattendue : " + JSON.stringify(result));
      } catch (error) {
        console.error("Erreur lors de l'analyse :", error);
        alert("Erreur lors du lancement de l'analyse");
      }
      isAnalyzing = false;
    }
  
    async function startRecommendation() {
      isRecommending = true;
      try {
        const response = await fetch("/recommend");
        const result = await response.json();
        console.log("Recommandations :", result);
        alert(result.message ?? "Réponse inattendue : " + JSON.stringify(result));
      } catch (error) {
        console.error("Erreur lors de la recommandation :", error);
        alert("Erreur lors du déclenchement des recommandations");
      }
      isRecommending = false;
    }
  </script>
  
  <div class="data-actions">
    <button on:click={startCollection} disabled={isCollecting}>
      {isCollecting ? "Collecte en cours..." : "Démarrer la collecte"}
    </button>
  
    <button on:click={startAnalysis} disabled={isAnalyzing}>
      {isAnalyzing ? "Analyse en cours..." : "Lancer l'analyse"}
    </button>
  
    <button on:click={startRecommendation} disabled={isRecommending}>
      {isRecommending ? "Recommandation en cours..." : "Recommander des images"}
    </button>
  </div>
  
  <style>
    .data-actions {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin: 1rem 0;
      flex-wrap: wrap;
    }
  
    button {
      padding: 0.5rem 1rem;
      border-radius: 6px;
      background-color: #007acc;
      color: white;
      border: none;
      cursor: pointer;
    }
  
    button:disabled {
      background-color: #999;
      cursor: not-allowed;
    }
  </style>
  