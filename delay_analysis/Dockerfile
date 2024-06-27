FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update

COPY . /home/app

RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port que Streamlit va utiliser
EXPOSE 8501

# Définir la commande par défaut pour démarrer l'application Streamlit
CMD ["sh", "-c", "streamlit run app.py --server.port $PORT"]
#CMD streamlit run --server.port $PORT app.py 