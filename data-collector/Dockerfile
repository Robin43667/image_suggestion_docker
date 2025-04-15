# Dockerfile - data-collector

FROM python:3.11-slim

# Crée un dossier de travail dans le conteneur
WORKDIR /app

# Copie les fichiers de l'application dans le conteneur
COPY . .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Démarre l'application
CMD ["python", "app.py"]
