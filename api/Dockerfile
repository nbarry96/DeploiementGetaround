FROM continuumio/miniconda3

WORKDIR /home/app

# Mettre à jour le système et installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y nano unzip curl build-essential

# Installer une version spécifique de Python (par exemple, Python 3.8)
RUN conda install -y python=3.8

# Installer Deta CLI
RUN curl -fsSL https://get.deta.dev/cli.sh | sh

# Copier les dépendances et les installer
COPY requirements.txt /dependencies/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /dependencies/requirements.txt

# Copier le reste des fichiers de l'application dans le conteneur
COPY . /home/app

# Commande pour démarrer l'application
# Commande pour démarrer l'application FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4000"]