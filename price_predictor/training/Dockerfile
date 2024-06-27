FROM continuumio/miniconda3

WORKDIR /home/app

# Mettre à jour le système et installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y nano unzip curl build-essential

# Installer Deta CLI
RUN curl -fsSL https://get.deta.dev/cli.sh | sh

# Installer AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

# Copier les dépendances et les installer
COPY requirements.txt /dependencies/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /dependencies/requirements.txt

# Définir les variables d'environnement
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV BACKEND_STORE_URI=$BACKEND_STORE_URI
ENV ARTIFACT_STORE_URI=$ARTIFACT_STORE_URI

# Commande pour démarrer le serveur MLflow
CMD mlflow server -p $PORT \
    --host 0.0.0.0 \
    --backend-store-uri $BACKEND_STORE_URI \
    --default-artifact-root $ARTIFACT_STORE_URI

    
FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update && \
    apt-get install -y nano unzip curl gcc

RUN curl -fsSL https://get.deta.dev/cli.sh | sh

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

COPY requirements.txt /dependencies/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /dependencies/requirements.txt

COPY train.py /home/app/train.py

ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV BACKEND_STORE_URI=$BACKEND_STORE_URI
ENV ARTIFACT_STORE_URI=$ARTIFACT_STORE_URI

CMD ["python", "/home/app/train.py"]