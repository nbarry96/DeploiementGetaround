# Prédiction des prix de location GetAround 🚘
L'objectif ici est d'entraîner des modèles de Machine Learning dans une application pour prédire le prix de location quotidien des voitures. Pour commencer, j'ai entraîné plusieurs modèles sur un serveur de suivi MLflow.

## Résultats
Vous pouvez accéder à l'application en ligne hébergeant le serveur MLflow : https://mlflow-api-85ae755d001e.herokuapp.com/

## Exécution
### 1. Structure du projet

price_predictor


├── training

│   ├── Dockerfile

│   ├── requirements.txt

│   ├── run.sh

│   └── train.py

└── tracking_server_setup

    ├── Dockerfile 
    
    ├── requirements.txt
    
    └── run.sh


### 2. Prérequis - Installations
* Avoir un éditeur de code (Visual Studio Code par exemple)

## 3. Déployer l'application vers heroku
Placez-vous dans le répertoire `tracking_serveur_setup`
```bash
cd DeploiementGetaround/price_predictor/tracking_serveur_setup/
```
Créez l'application Heroku hébergeant le serveur MLflow
```bash
heroku create <YOUR_APP_NAME>
```
Construire et faire un push de l'image Docker vers heroku
```bash
heroku container:push web -a <YOUR_APP_NAME>
```
Déployer l'image Docker vers heroku.
```bash
heroku container:release web -a <YOUR_APP_NAME>
```
## 5. Entrainez les modèles
Placez-vous dans le répertoire `training`
```bash
cd DeploiementGetaround/price_predictor/training/
```
* Ouvrez le fichier run.sh et Remplacez les variables d'environnement par leurs valeurs spécifiques :
APP_URI=your_app_uri_here

AWS_ACCESS_KEY_ID="your_access_key_id_here" 

AWS_SECRET_ACCESS_KEY="your_secret_access_key_here" 

1. **APP_URI** : Il s'agit de l'URI (Uniform Resource Identifier) l'application MLflow crée sur Heroku. 
  
2. **AWS_ACCESS_KEY_ID** et **AWS_SECRET_ACCESS_KEY** : Ce sont les identifiants et clés d'accès AWS nécessaires pour authentifier et accéder aux services AWS à partir l'application.

* Créer une images docker avec le Dockerfile
docker build . -t <YOUR_Docker_NAME>

* Exécuter run.sh
```bash
chmod +X run.sh
./run.sh
```
Les résultats seront automatiquement enregistrés sur le serveur MLFlow. Vous pouvez exécuter les différents modèles en sélectionnant celui que vous souhaitez entraîner dans le fichier run.sh.

## Source de données
Le jeu de données utilisé pour ce projet est fourni par Jedha Bootcamp et est disponible [ici](https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv)
