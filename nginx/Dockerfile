# Étape 1 : Build du frontend avec Node
FROM node:20-alpine AS builder

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend ./
RUN npm run build

# Étape 2 : Serveur NGINX pour servir le frontend
FROM nginx:alpine

# Copier les fichiers construits dans le dossier nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copier la configuration NGINX
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
