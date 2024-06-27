import gc
import uvicorn
import numpy as np
import pandas as pd
from pydantic import BaseModel
from typing import Literal
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from joblib import load

# Description pour l'application FastAPI
description = """
Bienvenue sur l'API de prédiction de prix de location GetAround !\n
Soumettez les caractéristiques de votre voiture pour obtenir une estimation du prix de location quotidien, basée sur l'un des trois modèles pré-entraînés : Régression Linéaire, Régression Ridge ou Forêt Aléatoire.

**Utilisez l'endpoint /predict pour estimer le prix de location de votre voiture !**
"""

# Métadonnées pour les tags FastAPI
tags_metadata = [
    {
        "name": "Prédictions",
        "description": "Point de terminaison pour obtenir des prédictions."
    }
]

# Instanciation de l'application FastAPI
app = FastAPI(
    title="Prédicteur de prix de location de voiture",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata
)

# Définition de la classe Car pour les données d'entrée
class Car(BaseModel):
    model_key: Literal['Citroën', 'Peugeot', 'PGO', 'Opel', 'Renault', 'Audi', 'BMW', 'Mercedes', 'Volkswagen', 'Ferrari', 'SEAT', 'Mitsubishi', 'Nissan', 'Subaru', 'Toyota', 'other']
    mileage: float
    engine_power: float
    fuel: Literal['diesel', 'petrol', 'hybrid_petrol', 'electro']
    paint_color: Literal['black', 'grey', 'white', 'red', 'silver', 'blue', 'beige', 'brown', 'green', 'orange']
    car_type: Literal['coupe', 'estate', 'hatchback', 'sedan', 'subcompact', 'suv', 'van', 'convertible']
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

# Rediriger automatiquement vers /docs (sans montrer cet endpoint dans /docs)
@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')

# Fonction pour charger le jeu de données
def load_data(url: str) -> pd.DataFrame:
    print("Chargement du jeu de données depuis l'URL...")
    dataset = pd.read_csv(url)
    dataset = dataset.drop(['Unnamed: 0'], axis=1)
    print("Jeu de données chargé avec succès.")
    return dataset

# URL du jeu de données
dataset_url = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv"
# Chargement du jeu de données
dataset = load_data(dataset_url)

# Définition du point de terminaison pour la prédiction
@app.post("/predict", tags=["Prédictions"])
async def predict(data: Car, regressor: str):
    # Nettoyer la mémoire inutilisée
    gc.collect(generation=2)

    # Charger le modèle approprié en fonction de 'regressor'
    if regressor == 'LR':
        loaded_model = load('LR_model.joblib')
    elif regressor == 'Ridge':
        loaded_model = load('Ridge_model.joblib')
    elif regressor == 'RF':
        loaded_model = load('RF_model.joblib')
    else:
        return {"error": f"Regressor '{regressor}' not supported."}

    # Création d'un DataFrame à partir des nouvelles données
    new_data = pd.DataFrame([data.dict()])

    # Prédiction avec le modèle chargé
    predicted_price = loaded_model.predict(new_data)[0]  # Obtenir la prédiction

    return {"prediction": float(predicted_price)}  # Assurez-vous que predicted_price est de type float

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
