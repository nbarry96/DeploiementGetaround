# API pour la rédiction des prix de location GetAround 🚗
L'objectif ici est de déployer une API pour le meilleur modèle afin de faire des prédictions sur les données soumises à l'application. J'ai développé une API basée sur les trois modèles pré-entraînés avec FastAPI. Pour chaque modèle, le meilleur en termes d'hyperparamètres ajustés a été choisi. Cette interface permet aux utilisateurs de faire des requêtes et d'obtenir rapidement des prédictions actualisées sur les prix de location de voitures.

## Résultats
Vous pouvez accéder à l'application en ligne hébergeant le serveur MLflow :

## Exécution
### 1. Structure du projet
- **Dockerfile**: Ce fichier contient les instructions pour construire l'image Docker du projet.
- **main.py**: Code principal de l'application, gérant les requêtes HTTP et l'intégration avec les modèles.
- **train.py**: Ce fichier contient le code pour l'entraînement des modèles.
- **requirements.txt**: Ce fichier liste toutes les dépendances et versions nécessaires pour exécuter le projet.
- **run.sh**: ce fichier contient les commandes et scripts nécessaires pour exécuter et démarrer le processus d'entraînement des modèles
- **LR_model.joblib, Ridge_model.joblib, RF_model.joblib** : Fichiers où sont enregistrés les meilleurs modèles entraînés.
- **README.md**: Ce fichier est la documentation principale du projet, fournissant des instructions d'installation, des exemples d'utilisation et d'autres informations pertinentes.

### 2. Prérequis - Installations
* Avoir un éditeur de code (Visual Studio Code par exemple)

## 4. Déployer l'application vers heroku
Placez-vous dans le répertoire `api`
```bash
cd DeploiementGetaround/api/
```
* Exécuter run.sh (cecode permet de d'exécuter les 3 modèles et sauvegarder les résultats des meilleurs hyperparamètres dans les fichiers .joblib)
```bash
chmod +X run.sh
./run.sh
```
*



## Source de données
Le jeu de données utilisé pour ce projet est fourni par Jedha Bootcamp et est disponible [ici](https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv)
