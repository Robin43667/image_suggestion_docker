# Système de Recommandation d'Images

## Objectif du projet

Ce projet vise à développer un système de recommandation d'images basé sur les préférences des utilisateurs. En utilisant des techniques d'analyse d'images, de clustering, de classification et d'apprentissage automatique, le projet permet de recommander des images similaires à celles que l'utilisateur aime, en se basant sur leurs caractéristiques visuelles.

## Sources de Données et Licence

Les données utilisées proviennent de **Wikidata** et sont sous licence libre. Nous avons collecté un total de **103 images** provenant de diverses catégories telles que **montagnes**, **nébuleuses**, **peintures** et **glaciers**. Ces images ont été téléchargées automatiquement à l'aide d'un script Python.

## Taille et Format des Données

Les images sont stockées dans un dossier local nommé `dataset`. Les métadonnées associées à chaque image sont centralisées dans un fichier JSON nommé `resultats_metadonnees.json`. Les informations contenues dans ce fichier incluent :

- Nom du fichier
- Extension et format de l’image (ex. `.jpg`, `.jpeg`)
- Dimensions de l’image (largeur et hauteur en pixels)
- Moyenne des 5 couleurs dominantes (calculée via l'algorithme KMeans)
- Données EXIF importantes (si disponibles)
- Tags associés à l’image (ex. #jpeg, #paysage)

## Préférences Utilisateur

Les utilisateurs saisissent leur nom et sélectionnent les images qu'ils préfèrent parmi une sélection aléatoire de 10 images. Ces préférences sont enregistrées dans un fichier JSON, `user_preferences.json`. Un autre script analyse ces préférences et crée un fichier `user_preferences_summary.json` qui synthétise les goûts visuels de chaque utilisateur.

### Rapports PDF

Pour chaque utilisateur, un rapport détaillé au format PDF est généré et inclut des visualisations comme des histogrammes, des nuages de mots et des graphiques de répartition des préférences visuelles.

## Algorithmes Utilisés

### 1. **Distance des Couleurs (Content-Based Filtering)**
Une comparaison est effectuée entre les couleurs dominantes des images préférées de l'utilisateur et celles du dataset à l'aide de la distance euclidienne. Les 5 images les plus similaires sont recommandées.

### 2. **Perceptron**
Le perceptron est un algorithme de classification supervisée linéaire utilisé pour prédire les images susceptibles d'être aimées par l'utilisateur, en fonction de leurs caractéristiques visuelles (couleurs dominantes, résolution, etc.).

### 3. **RandomForestClassifier**
L'algorithme Random Forest utilise un ensemble d'arbres de décision pour prédire les préférences visuelles de l'utilisateur. Il est plus robuste face à des données bruitées et non linéaires que le perceptron.

### 4. **KMeans (Clustering)**
KMeans est utilisé pour regrouper les images en 10 clusters en fonction de leurs caractéristiques visuelles. Lorsqu'un utilisateur aime une image, des images provenant du même cluster sont recommandées.

## Installation

Le dossier du projet est fourni sans le dataset et l'environnement virtuel contenant les dépendances nécessaires. Cependant, il inclut les résultats des utilisateurs testés précédemment, sous forme de fichiers JSON et PDF.

### Remarques importantes :
- Si vous souhaitez repartir de zéro, il est recommandé de supprimer tous les fichiers JSON, à moins que vous ne souhaitiez les compléter. Les fichiers PDF peuvent également être supprimés, mais ils seront automatiquement remplacés s'ils portent le même nom.

### Étapes d'installation :
1. Ouvrez un terminal à la racine du projet.
2. Créez un environnement virtuel avec la commande suivante :
```bash
   python -m venv venv
```
3. Activez l'environnement virtuel.
```bash
    venv\Scripts\activate
```
4. Installez les dépendances nécessaires à partir du fichier `requirements.txt` avec la commande suivant ou bien executer le premier bloc de code de ce notebook :
```bash
   pip install -r requirements.txt
```
5. Lancez Jupyter Notebook.
```bash
   jupyter notebook
```

Le téléchargement des images du dataset peut prendre un certain temps, c'est tout à fait normal. Une fois le téléchargement terminé, il vous suffira d'exécuter les blocs de code dans l'ordre et les rapports seront générés au fur et à mesure de l'exécution.
