import pandas as pd
from joblib import load
from pydantic import BaseModel, Field, Literal
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder


# Définition d'une classe pour les données d'entrée
class RequestCar(BaseModel):
    model_key: Literal['Citroën', 'Peugeot', 'PGO', 'Opel', 'Renault', 'Audi', 'BMW', 'Mercedes', 'Volkswagen', 'Ferrari', 'SEAT', 'Mitsubishi', 'Nissan', 'Subaru', 'Toyota', 'other']
    mileage: Union[int, float]
    engine_power: Union[int, float]
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

# Chargement du jeu de données
def load_data(url):
    print("Chargement du jeu de données depuis l'URL...")
    dataset = pd.read_csv(url)
    dataset = dataset.drop(['Unnamed: 0'], axis=1)
    print("Jeu de données chargé avec succès.")
    return dataset

# Chargement du jeu de données
dataset_url = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv"
dataset = load_data(dataset_url)

# Création d'une instance FastAPI
app = FastAPI(
    title="Prédiction de prix de location GetAround",
    description="""Bienvenue sur l'API de prédiction de prix de location GetAround !

Soumettez les caractéristiques de votre voiture pour obtenir une estimation du prix de location quotidien, basée sur l'un des trois modèles pré-entraînés : Régression Linéaire, Régression Ridge ou Forêt Aléatoire.

**Utilisez l'endpoint `/predict` pour estimer le prix de location de votre voiture !**
""",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Prédictions",
            "description": "Point de terminaison pour obtenir des prédictions."
        }
    ]
)

# Définition du point de terminaison pour la prédiction
@app.post("/predict")
async def predict(data: RequestCar, regressor: str):
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
    new_data = pd.DataFrame({
        "model_key": [data.model_key],
        "mileage": [data.mileage],
        "engine_power": [data.engine_power],
        "fuel": [data.fuel],
        "paint_color": [data.paint_color],
        "car_type": [data.car_type],
        "private_parking_available": [data.private_parking_available],
        "has_gps": [data.has_gps],
        "has_air_conditioning": [data.has_air_conditioning],
        "automatic_car": [data.automatic_car],
        "has_getaround_connect": [data.has_getaround_connect],
        "has_speed_regulator": [data.has_speed_regulator],
        "winter_tires": [data.winter_tires]
    })

    # Prédiction avec le modèle chargé
    class_idx = int(loaded_model.predict(new_data)[0])  # Convertir en entier

    # Vérification de la validité de l'index
    if 0 <= class_idx < len(dataset):
        predicted_price = dataset.iloc[class_idx]['rental_price_per_day']
        return {"prediction": int(predicted_price)}  # Assurez-vous que predicted_price est de type int
    else:
        return {"error": f"Invalid prediction index: {class_idx}"}