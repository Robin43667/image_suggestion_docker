# # Dockerfile - image-recommender

# FROM python:3.11-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir -r requirements.txt

# CMD ["python", "app.py"]


FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances nécessaires à Java et Spark
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jdk \
        procps \
        curl \
        gnupg \
        ca-certificates \
        apt-transport-https && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Définir JAVA_HOME pour PySpark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
