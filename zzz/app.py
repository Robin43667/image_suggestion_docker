import requests
import random
import os
import json
from PIL import Image
import exifread
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.linear_model import Perceptron
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from difflib import SequenceMatcher
import matplotlib.pyplot as plt
import cv2
from sklearn.cluster import KMeans
from IPython.display import display, Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from matplotlib.backends.backend_pdf import PdfPages
from collections import Counter
from matplotlib.patches import Rectangle
from wordcloud import WordCloud
import seaborn as sns
import json
import random
import numpy as np

Image.MAX_IMAGE_PIXELS = None


import os
import requests
import random

def telecharger_images_wikidata(requete_sparql, nombre_images, dossier_telechargement, prefixe):
    url_wikidata = "https://query.wikidata.org/sparql"
    params = {
        "query": requete_sparql,
        "format": "json",
    }

    try:
        reponse = requests.get(url_wikidata, params=params)
        reponse.raise_for_status()

        donnees = reponse.json()
        urls_images = [result["image"]["value"] for result in donnees["results"]["bindings"]]
        urls_images_aleatoires = random.sample(urls_images, min(nombre_images, len(urls_images)))

        os.makedirs(dossier_telechargement, exist_ok=True)

        for i, url_image in enumerate(urls_images_aleatoires):
            try:
                headers = {'User-Agent': 'MonProgrammePython/1.0 (test@example.com)'}
                reponse_image = requests.get(url_image, stream=True, headers=headers)
                reponse_image.raise_for_status()

                nom_fichier = os.path.join(dossier_telechargement, f"{prefixe}_{i+1}.jpg")
                with open(nom_fichier, "wb") as fichier:
                    for chunk in reponse_image.iter_content(chunk_size=8192):
                        fichier.write(chunk)

                print(f"Image {i+1} téléchargée : {nom_fichier}")

            except requests.exceptions.RequestException as e:
                print(f"Erreur lors du téléchargement de l'image {i+1} : {e}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête Wikidata : {e}")


requete_sparql_nebuleuses = """
SELECT ?image
WHERE {
  ?nebuleuse wdt:P31/wdt:P279* wd:Q204194 .
  ?nebuleuse wdt:P18 ?image .
}
LIMIT 35
"""

requete_sparql_glaciers = """
SELECT ?image
WHERE {
  ?glacier wdt:P31/wdt:P279* wd:Q35666 .
  ?glacier wdt:P18 ?image .
}
LIMIT 20
"""

requete_sparql_montagne = """
SELECT ?montagne ?montagneLabel ?image ?altitude ?coordonnees ?paysLabel
WHERE {
  ?montagne wdt:P31/wdt:P279* wd:Q8502. 
  ?montagne wdt:P18 ?image . 
  OPTIONAL { ?montagne wdt:P2044 ?altitude . } 
  OPTIONAL { ?montagne wdt:P625 ?coordonnees . } 
  OPTIONAL { ?montagne wdt:P17 ?pays . } 
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" . } 
}
LIMIT 35
"""

requete_sparql_peinture = """
SELECT ?peinture ?peintureLabel ?image ?artisteLabel ?dateCreation
WHERE {
  ?peinture wdt:P31 wd:Q3305213 .
  ?peinture wdt:P18 ?image .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" . }
}
LIMIT 20
"""

DOSSIER_TELECHARGEMENT = "dataset"

# Vérifie si le dossier existe et s'il est vide
if not os.path.exists(DOSSIER_TELECHARGEMENT) or not os.listdir(DOSSIER_TELECHARGEMENT):
    telecharger_images_wikidata(requete_sparql_nebuleuses, nombre_images=35, dossier_telechargement=DOSSIER_TELECHARGEMENT, prefixe="nebuleuse")
    telecharger_images_wikidata(requete_sparql_glaciers, nombre_images=20, dossier_telechargement=DOSSIER_TELECHARGEMENT, prefixe="glacier")
    telecharger_images_wikidata(requete_sparql_montagne, nombre_images=35, dossier_telechargement=DOSSIER_TELECHARGEMENT, prefixe="montagne")
    telecharger_images_wikidata(requete_sparql_peinture, nombre_images=20, dossier_telechargement=DOSSIER_TELECHARGEMENT, prefixe="peinture")
else :
  print(f"Le dossier '{DOSSIER_TELECHARGEMENT}' n'est pas vide. Téléchargement ignoré.")



from PIL import Image

os.environ["LOKY_MAX_CPU_COUNT"] = "1"

def get_dominant_colors(image_path, k=5):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image introuvable : {image_path}")
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (100, 100), interpolation=cv2.INTER_LINEAR)
        image = image.reshape((-1, 3))
        
        kmeans = KMeans(n_clusters=k, random_state=0, n_init=5)
        kmeans.fit(image)
        
        colors = kmeans.cluster_centers_.astype(int)
        return [(int(c[0]), int(c[1]), int(c[2])) for c in colors]
    except Exception as e:
        print(f"Erreur analyse couleur {image_path} : {e}")
        return [(0, 0, 0)] * k

def generate_tags(metadata):
    tags = set()
    if metadata.get("width") and metadata.get("height"):
        tags.add("#paysage" if metadata["width"] > metadata["height"] else "#portrait")
    if metadata.get("format"):
        tags.add(f"#{metadata['format'].lower()}")
    if "Make" in metadata.get("exifs", {}):
        tags.add(f"#{metadata['exifs']['Make'].lower()}")
    return list(tags)

def analyser_images(dossier_telechargement, fichier_sortie):
    resultats = []

    for fichier in os.listdir(dossier_telechargement):
        chemin_complet = os.path.join(dossier_telechargement, fichier)

        if os.path.isfile(chemin_complet) and fichier.lower().endswith(('.png', '.jpg', '.jpeg')):
            metadata = {
                'nom_fichier': fichier,
                'extension': os.path.splitext(fichier)[1].lower(),
                'format': '',
                'width': None,
                'height': None,
                'moyenne_couleur_rgb': [(0, 0, 0)] * 5,
                'exifs': {},
                'tags': []
            }

            # Lecture des dimensions et du format
            try:
                with Image.open(chemin_complet) as img:
                    metadata['width'], metadata['height'] = img.size
                    metadata['format'] = img.format
            except Exception as e:
                print(f"Erreur lors de l'ouverture de l'image {fichier} avec PIL : {e}")

            # Lecture des EXIFs
            try:
                with open(chemin_complet, 'rb') as f:
                    tags = exifread.process_file(f)
                    for tag in ['Image Make', 'Image Model', 'EXIF DateTimeOriginal']:
                        if tag in tags:
                            tag_key = tag.split()[-1]  # Simplifie : 'Make', 'Model', 'DateTimeOriginal'
                            metadata['exifs'][tag_key] = str(tags[tag])
            except Exception as e:
                print(f"Erreur lors de la lecture des métadonnées EXIF de {fichier} : {e}")

            # Couleurs dominantes
            metadata['moyenne_couleur_rgb'] = get_dominant_colors(chemin_complet, k=5)

            # Tags
            metadata['tags'] = generate_tags(metadata)

            resultats.append(metadata)

    # Écriture du fichier JSON
    try:
        os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
        with open(fichier_sortie, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=4, ensure_ascii=False)
        print(f"Métadonnées enrichies sauvegardées dans {fichier_sortie}")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier JSON : {e}")

DOSSIER_TELECHARGEMENT = "dataset"
FICHIER_SORTIE = "export/resultats_metadonnees.json"

analyser_images(DOSSIER_TELECHARGEMENT, FICHIER_SORTIE)


from IPython.display import Image, display


def ask_user_preference(image_path):
    display(Image(filename=image_path))  
    response = input(f"Aimez-vous cette image {os.path.basename(image_path)} ? (oui/non): ").strip().lower()
    return response == 'oui'

user_name = input("Entrez votre nom: ").strip()

dataset_folder = "dataset"
json_file = "export/user_preferences.json"

if os.path.exists(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
else:
    user_data = {}

if user_name not in user_data:
    user_data[user_name] = []

all_images = [os.path.join(dataset_folder, f) for f in os.listdir(dataset_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
chosen_images = random.sample(all_images, 10)

for image_path in chosen_images:
    if ask_user_preference(image_path):
        user_data[user_name].append(os.path.basename(image_path))

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(user_data, f, indent=4, ensure_ascii=False)

print(f"Vos préférences ont été sauvegardées dans {json_file}.")


def analyser_preferences(metadata_file, preferences_file):
    if not os.path.exists(preferences_file):
        print("Fichier user_preferences.json introuvable.")
        return

    if not os.path.exists(metadata_file):
        print("Fichier resultats_metadonnees.json introuvable.")
        return

    with open(preferences_file, 'r', encoding='utf-8') as f:
        preferences_data = json.load(f)

    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata_list = json.load(f)

    user_syntheses = {}

    # Traitement des préférences pour chaque utilisateur
    for user_name, liked_images in preferences_data.items():
        print(f"Analyzing preferences for {user_name}...")
        
        liked_metadata = [m for m in metadata_list if m["nom_fichier"] in liked_images]

        if not liked_metadata:
            print(f"Aucun métadonnée trouvée pour l'utilisateur {user_name}.")
            continue

        # Analyse des préférences
        formats = Counter(m.get("format", "Inconnu") for m in liked_metadata)
        orientations = Counter(
            "Portrait" if m["height"] > m["width"] else "Paysage"
            for m in liked_metadata if m.get("width") and m.get("height")
        )

        all_colors = []
        all_tags = []
        width_total, height_total = 0, 0

        for m in liked_metadata:
            all_colors.extend(m.get("moyenne_couleur_rgb", []))
            all_tags.extend(m.get("tags", []))
            width_total += m.get("width", 0)
            height_total += m.get("height", 0)

        color_counter = Counter(tuple(c) for c in all_colors)
        tag_counter = Counter(all_tags)

        avg_resolution = {
            "width": int(width_total / len(liked_metadata)),
            "height": int(height_total / len(liked_metadata))
        }

        # Synthèse des préférences de l'utilisateur
        user_synthesis = {
            "formats": dict(formats),
            "orientations": dict(orientations),
            "top_colors": color_counter.most_common(10),
            "top_tags": tag_counter.most_common(10),
            "avg_resolution": avg_resolution,
        }

        # Enregistrer la synthèse dans le dictionnaire principal
        user_syntheses[user_name] = user_synthesis

        export_path = f"export/analyzed_user_preferences/user_{user_name}_analyzed_preferences.pdf"
        os.makedirs("export", exist_ok=True)

        with PdfPages(export_path) as pdf:
            create_cover_page(user_name, pdf)
            create_table_of_contents(pdf)
            visualize_all_results(user_name, color_counter, tag_counter, avg_resolution, formats, orientations, pdf)

        print(f"Rapport PDF généré pour {user_name}: {export_path}")

    # Sauvegarder les synthèses dans un fichier JSON
    with open("export/user_preferences_summary.json", "w", encoding='utf-8') as f:
        json.dump(user_syntheses, f, ensure_ascii=False, indent=4)

    print("Synthèse des préférences utilisateurs enregistrée dans 'user_preferences_summary.json'.")


def create_cover_page(user_name, pdf):
    plt.figure(figsize=(8.5, 11))
    plt.text(0.5, 0.7, f"Rapport des préférences de l'utilisateur {user_name}", ha='center', va='center', fontsize=20, fontweight="bold")
    plt.text(0.5, 0.5, "Analysées sous forme de graphiques", ha='center', va='center', fontsize=16)
    plt.text(0.5, 0.35, "Outils utilisés:", ha='center', va='center', fontsize=14)
    plt.text(0.5, 0.2, "• Matplotlib", ha='center', va='center', fontsize=12)
    plt.text(0.5, 0.15, "• Seaborn", ha='center', va='center', fontsize=12)
    plt.text(0.5, 0.1, "• WordCloud", ha='center', va='center', fontsize=12)
    plt.text(0.5, 0.05, "• Python, JSON, etc.", ha='center', va='center', fontsize=12)
    
    plt.axis('off')
    pdf.savefig()
    plt.show()

def create_table_of_contents(pdf):
    plt.figure(figsize=(8.5, 11))
    plt.text(0.5, 0.9, "Table des matières", ha='center', va='center', fontsize=18, fontweight="bold")
    
    table_of_contents = [
        ("1. Page de garde", 0.85),
        ("2. Table des matières", 0.75),
        ("3. Formats d'image préférés", 0.65),
        ("4. Orientation préférée", 0.55),
        ("5. Top 10 des couleurs dominantes", 0.45),
        ("6. Histogramme des couleurs", 0.35),
        ("7. Nuage de mots des tags", 0.25),
        ("8. Résolution moyenne des images", 0.15),
    ]
    
    for item, y_pos in table_of_contents:
        plt.text(0.5, y_pos, item, ha='center', va='center', fontsize=14)

    plt.axis('off')
    pdf.savefig()
    plt.show()

def visualize_all_results(user_name, color_counter, tag_counter, avg_resolution, formats, orientations, pdf):
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(6, 4))
    plt.title("Formats d'image préférés")
    plt.bar(formats.keys(), formats.values(), color='skyblue')
    plt.xlabel("Format")
    plt.ylabel("Nombre de likes")
    plt.tight_layout()
    pdf.savefig()
    plt.show()

    plt.figure(figsize=(6, 4))
    plt.title("Orientation préférée")
    plt.bar(orientations.keys(), orientations.values(), color='salmon')
    plt.xlabel("Orientation")
    plt.ylabel("Nombre de likes")
    plt.tight_layout()
    pdf.savefig()
    plt.show()

    plt.figure(figsize=(10, 2))
    ax = plt.gca()
    top_colors = color_counter.most_common(10)
    for i, (color, count) in enumerate(top_colors):
        hex_color = "#{:02x}{:02x}{:02x}".format(*color)
        ax.add_patch(Rectangle((i, 0), 1, 1, color=hex_color))
        ax.text(i + 0.5, -0.2, f"{count}", ha='center', va='top', fontsize=10)
        ax.text(i + 0.5, 1.05, hex_color, ha='center', va='bottom', fontsize=8, rotation=45)
    ax.set_xlim(0, len(top_colors))
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.title("Top 10 couleurs dominantes")
    plt.tight_layout()
    pdf.savefig()
    plt.show()

    plt.figure(figsize=(10, 4))
    color_labels = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in color_counter.keys()]
    plt.bar(range(len(color_counter)), color_counter.values(), color=color_labels)
    plt.xlabel("Couleurs")
    plt.ylabel("Occurrences")
    plt.title(f"Histogramme des couleurs dominantes de {user_name}")
    plt.xticks([])
    plt.tight_layout()
    pdf.savefig()
    plt.show()

    plt.figure(figsize=(10, 6))
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(tag_counter)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(f"Nuage de tags préférés de {user_name}")
    plt.tight_layout()
    pdf.savefig()
    plt.show()

    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ["Largeur (px)", "Hauteur (px)"]
    values = [avg_resolution["width"], avg_resolution["height"]]
    colors = ["#4682B4", "#8B0000"]
    bars = ax.barh(categories, values, color=colors, edgecolor="black", height=0.5)
    for bar, value in zip(bars, values):
        ax.text(value + 200, bar.get_y() + bar.get_height() / 2, f"{value} px", va='center', fontsize=12, fontweight="bold")
    ax.set_xlim(0, max(values) * 1.2)
    ax.set_xlabel("Résolution en pixels")
    ax.set_title(f"Résolution moyenne des images aimées par {user_name}")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    pdf.savefig()
    plt.show()

if __name__ == "__main__":
    analyser_preferences(
        metadata_file="export/resultats_metadonnees.json",
        preferences_file="export/user_preferences.json"
    )


from PIL import Image

with open('export/resultats_metadonnees.json', 'r') as f:
    images_metadata = json.load(f)

with open('export/user_preferences_summary.json', 'r') as f:
    user_preferences = json.load(f)

def trouver_image_reference(user_name, images_metadata):
    # Récupérer les préférences de l'utilisateur
    preferences = user_preferences.get(user_name, {})
    
    # Si l'utilisateur n'a pas de préférences, on retourne une image aléatoire
    if not preferences:
        print(f"Aucune préférence trouvée pour l'utilisateur {user_name}, sélection aléatoire d'une image.")
        return random.choice(images_metadata)
    
    top_colors = [color for color, _ in preferences.get("top_colors", [])]
    top_colors_array = np.array(top_colors)
    
    if top_colors_array.shape[0] > 5:
        top_colors_array = top_colors_array[:5] 
    elif top_colors_array.shape[0] < 5:
        top_colors_array = np.tile(top_colors_array, (5 // top_colors_array.shape[0], 1))[:5]

    meilleures_distances = []
    
    for image in images_metadata:
        image_rgb = np.array(image["moyenne_couleur_rgb"]).reshape(1, -1)
        
        distances = euclidean_distances(image_rgb, top_colors_array.reshape(1, -1))  
        meilleures_distances.append((image, distances.min()))  
    
    meilleures_distances.sort(key=lambda x: x[1])
    
    return meilleures_distances[0][0]

def afficher_image_avec_couleurs(image_path, couleurs, titre):
    try:
        img = Image.open(image_path)
        fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1]}, figsize=(6, 7))

        ax[0].imshow(img)
        ax[0].set_title(titre)
        ax[0].axis('off')

        couleurs_array = np.zeros((50, 300, 3))
        segment_width = 300 // 5 

        for i in range(5):
            couleurs_array[:, i * segment_width:(i + 1) * segment_width] = np.array(couleurs[i]) / 255

        ax[1].imshow(couleurs_array)
        ax[1].set_xticks([])
        ax[1].set_yticks([])

        plt.show()
    except Exception as e:
        print(f"Erreur lors de l'affichage de l'image {image_path} : {e}")

for user_name in user_preferences.keys():
    print(f"\nTraitement des préférences pour l'utilisateur {user_name}...")

    image_choisie = trouver_image_reference(user_name, images_metadata)
    image_rgb = np.array(image_choisie["moyenne_couleur_rgb"]).reshape(1, -1)
    images_rgb = np.array([
        np.array(image["moyenne_couleur_rgb"]).flatten() for image in images_metadata
    ])

    distances = euclidean_distances(image_rgb, images_rgb)
    indices_similaires = np.argsort(distances[0])

    image_path_choisie = f"dataset/{image_choisie['nom_fichier']}"
    afficher_image_avec_couleurs(
        image_path_choisie,
        image_choisie["moyenne_couleur_rgb"],
        f"Image de référence pour {user_name} : {image_choisie['nom_fichier']}"
    )

    # Affichage des 5 images similaires
    print(f"Recommandations d'images similaires pour {user_name} :")
    for i in range(1, 6): 
        image_similaire = images_metadata[indices_similaires[i]]
        image_path_similaire = f"dataset/{image_similaire['nom_fichier']}"
        
        couleurs_principales = image_similaire["moyenne_couleur_rgb"]
        
        titre = f"{image_similaire['nom_fichier']} (distance={distances[0][indices_similaires[i]]:.2f})"
        afficher_image_avec_couleurs(
            image_path_similaire,
            couleurs_principales,
            titre
        )


from PIL import Image

with open('export/resultats_metadonnees.json', 'r') as f:
    images_metadata = json.load(f)

with open('export/user_preferences_summary.json', 'r') as f:
    user_preferences = json.load(f)

def similarité_nom_fichier(nom1, nom2):
    return SequenceMatcher(None, nom1, nom2).ratio()

def similarité_extension(ext1, ext2):
    return 1 if ext1 == ext2 else 0

def distance_moyenne_couleurs(couleurs1, couleurs2):
    couleurs1 = np.array(couleurs1)
    couleurs2 = np.array(couleurs2)
    return np.mean(np.linalg.norm(couleurs1 - couleurs2, axis=1))

def trouver_image_reference(user_name, images_metadata):
    preferences = user_preferences.get(user_name, {})
    
    # Si l'utilisateur n'a pas de préférences, on retourne une image aléatoire
    if not preferences:
        print(f"Aucune préférence trouvée pour l'utilisateur {user_name}, sélection aléatoire d'une image.")
        return random.choice(images_metadata)
    
    top_colors = [color for color, _ in preferences.get("top_colors", [])]
    top_colors_array = np.array(top_colors)
    
    if top_colors_array.shape[0] > 5:
        top_colors_array = top_colors_array[:5]  
    elif top_colors_array.shape[0] < 5:
        top_colors_array = np.tile(top_colors_array, (5 // top_colors_array.shape[0], 1))[:5]

    meilleures_distances = []
    
    for image in images_metadata:
        image_rgb = np.array(image["moyenne_couleur_rgb"]).reshape(1, -1)
        distances = euclidean_distances(image_rgb, top_colors_array.reshape(1, -1))  
        meilleures_distances.append((image, distances.min())) 
    
    meilleures_distances.sort(key=lambda x: x[1])
    
    return meilleures_distances[0][0]

# Entraînement du modèle 
X = []
y = []

models_info = {}

for user_name in user_preferences.keys():
    print(f"\nTraitement des préférences pour l'utilisateur {user_name}...")

    image_choisie = trouver_image_reference(user_name, images_metadata)

    X = []
    y = []

    for image in images_metadata:
        if image_choisie != image:
            features = []

            couleur_choisie = np.array(image_choisie["moyenne_couleur_rgb"]).flatten()
            couleur_image = np.array(image["moyenne_couleur_rgb"]).flatten()

            features.extend(couleur_choisie)
            features.extend(couleur_image)

            features.append(similarité_nom_fichier(image_choisie["nom_fichier"], image["nom_fichier"]))
            features.append(similarité_extension(image_choisie["extension"], image["extension"]))

            X.append(features)

            distance_couleurs = distance_moyenne_couleurs(
                image_choisie["moyenne_couleur_rgb"],
                image["moyenne_couleur_rgb"]
            )
            y.append(1 if distance_couleurs < 150 else 0)

    X = np.array(X)
    y = np.array(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    filtered_metadata = [image for image in images_metadata if image != image_choisie]

    X_train, X_test, y_train, y_test, metadata_train, metadata_test = train_test_split(
        X_scaled, y, filtered_metadata, test_size=0.2, random_state=42
    )

    model = Perceptron(max_iter=1000, eta0=0.1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Précision du modèle pour {user_name} : {accuracy:.2f}")

    models_info[user_name] = {
        "model": model,
        "scaler": scaler,
        "image_choisie": image_choisie,
        "y_test": y_test,
        "y_pred": y_pred,
        "accuracy": accuracy,
        "metadata_test": metadata_test,
    }


for user_name, info in models_info.items():
    pdf_filename = f"export/perceptron/{user_name}_perceptron.pdf"
    with PdfPages(pdf_filename) as pdf:
        accuracy = info["accuracy"]
        y_pred = info["y_pred"]
        image_choisie = info["image_choisie"]

        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.8, f"Recommandations d'images pour {user_name}", horizontalalignment='center', fontsize=16, weight='bold')
        plt.text(0.5, 0.6, f"Modèle utilisé : Perceptron", horizontalalignment='center', fontsize=12, style='italic')
        plt.text(0.5, 0.4, f"Précision du modèle : {accuracy:.2f}", horizontalalignment='center', fontsize=12, weight='bold')
        plt.axis('off')
        pdf.savefig()
        plt.close()

        image_path_choisie = f"dataset/{image_choisie['nom_fichier']}"
        img_choisie = Image.open(image_path_choisie)

        plt.figure(figsize=(6, 6))
        plt.imshow(img_choisie)
        plt.title(f"Image de référence : {image_choisie['nom_fichier']}")
        plt.axis('off')
        pdf.savefig() 
        plt.close()

        # Images similaires
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.8, "Images similaires :", horizontalalignment='center', fontsize=14, weight='bold')
        plt.axis('off')
        pdf.savefig() 
        plt.close()

        count = 0
        metadata_test = info["metadata_test"]
        for i, prediction in enumerate(y_pred):
            if prediction == 1 and count < 10:
                image_similaire = metadata_test[i]
                image_path_similaire = f"dataset/{image_similaire['nom_fichier']}"
                img_similaire = Image.open(image_path_similaire)

                plt.figure(figsize=(6, 6))
                plt.imshow(img_similaire)
                plt.title(f"{image_similaire['nom_fichier']}")
                plt.axis('off')
                pdf.savefig()  
                plt.close()

                count += 1

    print(f"Rapport généré pour {user_name} : {pdf_filename}")


from PIL import Image
Image.MAX_IMAGE_PIXELS = None 

# Chargement des métadonnées
with open('export/resultats_metadonnees.json', 'r') as f:
    images_metadata = json.load(f)

with open('export/user_preferences_summary.json', 'r') as f:
    user_preferences = json.load(f)

# Fonction de similarité
def similarité_nom_fichier(nom1, nom2):
    return SequenceMatcher(None, nom1, nom2).ratio()

def similarité_extension(ext1, ext2):
    return 1 if ext1 == ext2 else 0

def distance_moyenne_couleurs(couleurs1, couleurs2):
    couleurs1 = np.array(couleurs1)
    couleurs2 = np.array(couleurs2)
    return np.mean(np.linalg.norm(couleurs1 - couleurs2, axis=1))

# Trouver l'image de référence basée sur les préférences de l'utilisateur
def trouver_image_reference(user_name, images_metadata):
    preferences = user_preferences.get(user_name, {})
    
    if not preferences:
        print(f"Aucune préférence trouvée pour l'utilisateur {user_name}, sélection aléatoire d'une image.")
        return random.choice(images_metadata)
    
    top_colors = [color for color, _ in preferences.get("top_colors", [])]
    top_colors_array = np.array(top_colors)
    
    if top_colors_array.shape[0] > 5:
        top_colors_array = top_colors_array[:5]  
    elif top_colors_array.shape[0] < 5:
        top_colors_array = np.tile(top_colors_array, (5 // top_colors_array.shape[0], 1))[:5]

    meilleures_distances = []
    
    for image in images_metadata:
        image_rgb = np.array(image["moyenne_couleur_rgb"]).reshape(1, -1)
        distances = euclidean_distances(image_rgb, top_colors_array.reshape(1, -1))  
        meilleures_distances.append((image, distances.min()))  
    
    meilleures_distances.sort(key=lambda x: x[1])
    
    return meilleures_distances[0][0]

# Entraînement du modèle
X = []
y = []
features_list = []
metadata_list = []

for user_name in user_preferences.keys():
    print(f"\nTraitement des préférences pour l'utilisateur {user_name}...")

    image_choisie = trouver_image_reference(user_name, images_metadata)

    for image in images_metadata:
        if image_choisie != image:
            couleur_choisie = np.array(image_choisie["moyenne_couleur_rgb"]).flatten()
            couleur_image = np.array(image["moyenne_couleur_rgb"]).flatten()

            features = list(couleur_choisie) + list(couleur_image)
            features.append(similarité_nom_fichier(image_choisie["nom_fichier"], image["nom_fichier"]))
            features.append(similarité_extension(image_choisie["extension"], image["extension"]))

            distance_couleurs = distance_moyenne_couleurs(image_choisie["moyenne_couleur_rgb"], image["moyenne_couleur_rgb"])
            label = 1 if distance_couleurs < 150 else 0

            X.append(features)
            y.append(label)
            metadata_list.append(image)

X = np.array(X)
y = np.array(y)

X_train, X_test, y_train, y_test, metadata_train, metadata_test = train_test_split(
    X, y, metadata_list, test_size=0.3, random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Création du modèle RandomForestClassifier
model = RandomForestClassifier(n_estimators=150, max_depth=20, random_state=42, n_jobs=-1)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"Précision du modèle : {accuracy:.2f}")

# Entraînement du modèle pour chaque utilisateur
for user_name in user_preferences.keys():
    print(f"\nTraitement des préférences pour l'utilisateur {user_name}...")
    
    X_user = []
    y_user = []
    metadata_user = []

    image_choisie = trouver_image_reference(user_name, images_metadata)

    for image in images_metadata:
        if image_choisie != image:
            couleur_choisie = np.array(image_choisie["moyenne_couleur_rgb"]).flatten()
            couleur_image = np.array(image["moyenne_couleur_rgb"]).flatten()

            features = list(couleur_choisie) + list(couleur_image)
            features.append(similarité_nom_fichier(image_choisie["nom_fichier"], image["nom_fichier"]))
            features.append(similarité_extension(image_choisie["extension"], image["extension"]))

            distance_couleurs = distance_moyenne_couleurs(image_choisie["moyenne_couleur_rgb"], image["moyenne_couleur_rgb"])
            label = 1 if distance_couleurs < 150 else 0

            X_user.append(features)
            y_user.append(label)
            metadata_user.append(image)

    X_user = np.array(X_user)
    y_user = np.array(y_user)

    X_train_user, X_test_user, y_train_user, y_test_user, metadata_train_user, metadata_test_user = train_test_split(
        X_user, y_user, metadata_user, test_size=0.3, random_state=42
    )

    scaler_user = StandardScaler()
    X_train_user_scaled = scaler_user.fit_transform(X_train_user)
    X_test_user_scaled = scaler_user.transform(X_test_user)

    model_user = RandomForestClassifier(n_estimators=150, max_depth=20, random_state=42, n_jobs=-1)
    model_user.fit(X_train_user_scaled, y_train_user)

    y_pred_user = model_user.predict(X_test_user_scaled)
    accuracy_user = accuracy_score(y_test_user, y_pred_user)
    print(f"Précision du modèle pour {user_name} : {accuracy_user:.2f}")

    pdf_filename = f"export/randomForestClassifier/{user_name}_randomForestClassifier.pdf"
    with PdfPages(pdf_filename) as pdf:

        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.8, f"Recommandations d'images pour {user_name}", horizontalalignment='center', fontsize=16, weight='bold')
        plt.text(0.5, 0.6, f"Modèle utilisé : RandomForestClassifier", horizontalalignment='center', fontsize=12, style='italic')
        plt.text(0.5, 0.4, f"Précision du modèle : {accuracy_user:.2f}", horizontalalignment='center', fontsize=12, weight='bold') 
        plt.axis('off')
        pdf.savefig()  
        plt.close()

        image_choisie = trouver_image_reference(user_name, images_metadata)
        image_path_choisie = f"dataset/{image_choisie['nom_fichier']}"
        img_choisie = Image.open(image_path_choisie)

        plt.figure(figsize=(6, 6))
        plt.imshow(img_choisie)
        plt.title(f"Image de référence : {image_choisie['nom_fichier']}")
        plt.axis('off')
        pdf.savefig()  
        plt.close()

        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.8, "Images similaires :", horizontalalignment='center', fontsize=14, weight='bold')
        plt.axis('off')
        pdf.savefig()  
        plt.close()

        X_test_images_user = []
        for image in images_metadata:
            if image != image_choisie: 
                features = []
                features.extend(np.array(image_choisie["moyenne_couleur_rgb"]).flatten())
                features.extend(np.array(image["moyenne_couleur_rgb"]).flatten())
                features.append(similarité_nom_fichier(image_choisie["nom_fichier"], image["nom_fichier"]))
                features.append(similarité_extension(image_choisie["extension"], image["extension"]))
                X_test_images_user.append(features)

        X_test_images_user_scaled = scaler_user.transform(X_test_images_user)

        y_pred_images_user = model_user.predict(X_test_images_user_scaled)

        count = 0
        for i, prediction in enumerate(y_pred_images_user):
            if prediction == 1 and count < 10:  
                image_similaire = metadata_test_user[i]
                image_path_similaire = f"dataset/{image_similaire['nom_fichier']}"
                if os.path.exists(image_path_similaire):
                    img_similaire = Image.open(image_path_similaire)
                    plt.figure(figsize=(6, 6))
                    plt.imshow(img_similaire)
                    plt.title(f"{image_similaire['nom_fichier']}")
                    plt.axis('off')
                    pdf.savefig()  
                    plt.close()
                    count += 1

    print(f"Rapport généré pour {user_name} : {pdf_filename}")


from PIL import Image
Image.MAX_IMAGE_PIXELS = None

with open('export/resultats_metadonnees.json', 'r') as f:
    images_metadata = json.load(f)

with open('export/user_preferences_summary.json', 'r') as f:
    user_preferences = json.load(f)

def similarité_nom_fichier(nom1, nom2):
    return SequenceMatcher(None, nom1, nom2).ratio()

def similarité_extension(ext1, ext2):
    return 1 if ext1 == ext2 else 0

def distance_moyenne_couleurs(couleurs1, couleurs2):
    couleurs1 = np.array(couleurs1)
    couleurs2 = np.array(couleurs2)
    return np.mean(np.linalg.norm(couleurs1 - couleurs2, axis=1))

def trouver_image_reference(user_name, images_metadata):
    preferences = user_preferences.get(user_name, {})
    
    if not preferences:
        print(f"Aucune préférence trouvée pour l'utilisateur {user_name}, sélection aléatoire d'une image.")
        return random.choice(images_metadata)
    
    top_colors = [color for color, _ in preferences.get("top_colors", [])]
    top_colors_array = np.array(top_colors)
    
    if top_colors_array.shape[0] > 5:
        top_colors_array = top_colors_array[:5]  
    elif top_colors_array.shape[0] < 5:
        top_colors_array = np.tile(top_colors_array, (5 // top_colors_array.shape[0], 1))[:5]

    meilleures_distances = []
    
    for image in images_metadata:
        image_rgb = np.array(image["moyenne_couleur_rgb"]).reshape(1, -1)
        
        distances = euclidean_distances(image_rgb, top_colors_array.reshape(1, -1))  
        meilleures_distances.append((image, distances.min()))  
    
    meilleures_distances.sort(key=lambda x: x[1])
    
    return meilleures_distances[0][0]

# === Clustering ===
# Construction des features
X = []
image_names = []

for image in images_metadata:
    features = []
    features.extend(np.array(image["moyenne_couleur_rgb"]).flatten())
    features.append(len(image["nom_fichier"]))
    features.append(similarité_extension(image["extension"], 'jpg'))  
    X.append(features)
    image_names.append(image["nom_fichier"])

X = np.array(X)

# Normalisation des features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Réduction de dimension avec PCA
pca = PCA(n_components=10)
X_pca = pca.fit_transform(X_scaled)

# Clustering avec KMeans
n_clusters = 10  
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
clusters = kmeans.fit_predict(X_pca)

# Ajout des résultats dans les métadonnées
for i, image in enumerate(images_metadata):
    image['cluster'] = clusters[i]

# Regrouper les images par cluster
clusters_dict = {i: [] for i in range(n_clusters)}
for image in images_metadata:
    clusters_dict[image['cluster']].append(image)

os.makedirs('export/clusters', exist_ok=True)

for user_name in user_preferences.keys():
    pdf_filename = f"export/clusters/{user_name}_clusters.pdf"
    with PdfPages(pdf_filename) as pdf:

        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.8, f"Recommandations d'images pour {user_name}", horizontalalignment='center', fontsize=16, weight='bold')
        plt.text(0.5, 0.6, f"Utilisation de la méthode des Clusters", horizontalalignment='center', fontsize=12, style='italic')
        plt.axis('off')
        pdf.savefig()  
        plt.close()

        # Graphique en camembert pour les clusters
        plt.figure(figsize=(8, 6))
        cluster_counts = [0] * n_clusters
        for image in images_metadata:
            cluster_counts[image['cluster']] += 1
        
        plt.pie(cluster_counts, labels=[f"Cluster {i}" for i in range(n_clusters)], autopct='%1.1f%%', startangle=90)
        plt.title("Répartition des images par cluster")
        plt.axis('equal')  
        pdf.savefig()  
        plt.close()

        image_choisie = trouver_image_reference(user_name, images_metadata)
        image_path_choisie = f"dataset/{image_choisie['nom_fichier']}"
        img_choisie = Image.open(image_path_choisie)

        image_path_choisie = f"dataset/{image_choisie['nom_fichier']}"
        img_choisie = Image.open(image_path_choisie)
        img_choisie.thumbnail((256, 256))

        plt.figure(figsize=(6, 6))
        plt.imshow(img_choisie)
        plt.title(f"Image de référence : {image_choisie['nom_fichier']}")
        plt.axis('off')
        pdf.savefig()
        plt.close()

        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.8, "Images similaires :", horizontalalignment='center', fontsize=14, weight='bold')
        plt.axis('off')
        pdf.savefig()
        plt.close()

        similar_images = [img for img in clusters_dict[image_choisie['cluster']] if img != image_choisie]

        count = 0
        for image in similar_images[:10]:  
            image_path_similaire = f"dataset/{image['nom_fichier']}"
            img_similaire = Image.open(image_path_similaire)
            img_similaire.thumbnail((256, 256))

            plt.figure(figsize=(6, 6))
            plt.imshow(img_similaire)
            plt.title(f"{image['nom_fichier']}")
            plt.axis('off')
            pdf.savefig()
            plt.close()

            count += 1

    print(f"Rapport généré pour {user_name} : {pdf_filename}")
