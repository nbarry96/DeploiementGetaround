#!/bin/bash

# Installation des dépendances à partir du fichier requirements.txt
python3 -m pip install -r requirements.txt

# Exécution du script train.py pour différents modèles

# Modèle LR
python3 train.py --regressor LR --executor_name Nene --run_name LR_run

# Modèle Ridge avec différents arguments pour la régression Ridge
python3 train.py --regressor Ridge --alpha 0.5 1.0 1.5 --executor_name Nene --run_name Ridge_run

# Modèle Random Forest avec différents arguments pour Random Forest
python3 train.py --regressor RF --n_estimators 50 100 150 --max_depth 5 10 20 --min_samples_leaf 1 3 --executor_name Nene --run_name RF_run