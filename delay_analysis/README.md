# Tableau de bord : Analyse des retards de Getaround 🚗

Lorsqu'un utilisateur retarde le retour d'une voiture louée sur GetAround, cela peut perturber la disponibilité du véhicule pour les locations suivantes, affectant ainsi la qualité du service et la satisfaction des clients. L'objectif ici est de déployer un tableau de bord en ligne pour aider GetAround à  non seulemrnt Évaluer l'ampleur du problème, mais aussi Simuler les conséquences potentielles de l'instauration d'un délai minimal entre deux locations consécutives d'un même véhicule sur l'entreprise. 

## Resultats
Vous pouvez accéder au tableau de bord en ligne à cet emplacement : https://getearound-api-analysis-ac45266e0df6.herokuapp.com/

## Exécution
### 1. Structure du projet
- **Dockerfile**: Ce fichier contient les instructions pour construire l'image Docker du projet.
- **app.py**: Ce fichier contient le code principal de l'application.
- **requirements.txt**: Ce fichier liste toutes les dépendances et versions nécessaires pour exécuter le projet.
- **README.md**: Ce fichier est la documentation principale du projet, fournissant des instructions d'installation, des exemples d'utilisation et d'autres informations pertinentes.

### 2. Prérequis - Installations
* Avoir un éditeur de code (Visual Studio Code par exemple)
## 3. Dossier du projet
Clonez ce dépôt pour créer votre dossier de projet :
`git clone https://github.com/nbarry96/DeploiementGetaround.git`

## 4. Créer et déployer l'application vers heroku

Placez-vous dans le répertoire du projet `DeploiementGetaround`

```bash
cd DeploiementGetaround/delay-analysis/
```

Créez l'application Heroku hébergeant l'application
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

## Source de données
Le jeu de données utilisé pour ce projet est fourni par Jedha Bootcamp et est disponible [ici](https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx).

