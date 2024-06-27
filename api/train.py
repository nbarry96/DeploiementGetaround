import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, FunctionTransformer, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error
from joblib import dump
import argparse

# Fonction pour charger les données
def load_data(url):
    print("Loading dataset from URL...")
    dataset = pd.read_csv(url)
    dataset = dataset.drop(['Unnamed: 0'], axis=1)
    print("Dataset loaded successfully.")
    return dataset

# Fonction pour regrouper les catégories rares
def regroup_categories(df, column, threshold):
    print(f"Regrouping rare categories in column: {column}...")
    counts = df[column].value_counts()
    infrequent_values = counts[counts < threshold].index
    df.loc[df[column].isin(infrequent_values), column] = 'Others'
    print(f"Categories regrouped in column: {column}.")
    return df

# Fonction pour créer les préprocesseurs de features
def create_preprocessor(X):
    numeric_features = []
    binary_features = []
    categorical_features = []

    for col, dtype in X.dtypes.items():
        if ('float' in str(dtype)) or ('int' in str(dtype)):
            numeric_features.append(col)
        elif ('bool' in str(dtype)):
            binary_features.append(col)
        else:
            categorical_features.append(col)

    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('encoder', OneHotEncoder(drop='first'))
    ])

    binary_transformer = FunctionTransformer(None)

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features),
            ('bin', binary_transformer, binary_features)
        ])
    
    return preprocessor

# Fonction pour définir et entraîner le modèle
def train_model(X_train, Y_train, X_test, Y_test, regressor, param_grid=None, cv=None):
    print("Creating preprocessors for numerical, categorical, and binary features...")
    preprocessor = create_preprocessor(X_train)
    print("Preprocessors created successfully.")
    
    print(f"Training model: {regressor}...")
    if regressor == 'LR':
        model = LinearRegression()
    elif regressor == 'Ridge':
        model = Ridge()
    elif regressor == 'RF':
        model = RandomForestRegressor()

    if param_grid:
        model = GridSearchCV(model, param_grid=param_grid, cv=cv, verbose=3)
        print("GridSearchCV is being used for hyperparameter tuning.")

    predictor = Pipeline(steps=[
        ('features_preprocessing', preprocessor),
        ("model", model)
    ])

    predictor.fit(X_train, Y_train)
    print(f"Model {regressor} trained successfully.")
    return predictor, model

def main():
    print("Starting main execution...")
    
    # Analyser les arguments de la ligne de commande
    parser = argparse.ArgumentParser()
    parser.add_argument("--regressor", default='LR', choices=['LR', 'Ridge', 'RF'])
    parser.add_argument("--cv", type=int, default=None)
    parser.add_argument("--alpha", type=float, nargs="*")
    parser.add_argument("--max_depth", type=int, nargs="*")
    parser.add_argument("--min_samples_leaf", type=int, nargs="*")
    parser.add_argument("--min_samples_split", type=int, nargs="*")
    parser.add_argument("--n_estimators", type=int, nargs="*")
    parser.add_argument("--executor_name", default='Unknown')
    parser.add_argument("--run_name", default='LR_run', help="Specify the name for the run.")
    args = parser.parse_args()
    print(f"Command line arguments parsed: {args}")

    # Chargement des données
    dataset_url = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv"
    dataset = load_data(dataset_url)

    # Filtrer les données
    print("Filtering data...")
    dataset = dataset[(dataset['mileage'] >= 0) & (dataset['engine_power'] != 0)]
    print("Data filtered successfully.")

    # Regrouper les catégories rares
    columns_to_regroup = ['model_key', 'fuel', 'paint_color', 'car_type']
    threshold = 0.005 * len(dataset)
    for col in columns_to_regroup:
        dataset = regroup_categories(dataset, col, threshold)

    # Séparer les features et la cible
    print("Separating features and target...")
    target_name = 'rental_price_per_day'
    Y = dataset.loc[:, target_name]
    X = dataset.drop(target_name, axis=1)
    print("Features and target separated successfully.")

    # Diviser le jeu de données en ensembles d'entraînement et de test
    print("Splitting data into train and test sets...")
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    print("Data split successfully.")

    # Entraîner le modèle
    param_grid = {key: getattr(args, key) for key in vars(args) if getattr(args, key) is not None and key not in ['cv', 'regressor', 'executor_name', 'run_name']}
    grid_search_done = False
    if args.regressor == 'LR':
        model = LinearRegression()
    else:
        regressor_args = {option: parameters for option, parameters in vars(args).items() if (parameters is not None and option not in ['cv', 'regressor', 'run_name', 'executor_name'])}
        regressor_params = {param_name: values for param_name, values in regressor_args.items()}
        if args.regressor == 'Ridge':
            regressor = Ridge()
        elif args.regressor == 'RF':
            regressor = RandomForestRegressor()
        model = GridSearchCV(regressor, param_grid=regressor_params, cv=args.cv, verbose=3)
        grid_search_done = True

    predictor, model = train_model(X_train, Y_train, X_test, Y_test, args.regressor,
                                   param_grid=param_grid if param_grid else None,
                                   cv=args.cv if grid_search_done else None)

    # Enregistrer les meilleurs paramètres pour GridSearch
    if isinstance(model, GridSearchCV):
        print("Best parameters found by GridSearchCV:")
        print(model.best_params_)

    # Faire des prédictions sur les ensembles d'entraînement et de test
    print("Making predictions...")
    Y_train_pred = predictor.predict(X_train)
    Y_test_pred = predictor.predict(X_test)
    print("Predictions made successfully.")

    # Enregistrer les métriques R2 et MAE
    print("Logging metrics...")
    print(f"Train R2 score: {r2_score(Y_train, Y_train_pred)}")
    print(f"Test R2 score: {r2_score(Y_test, Y_test_pred)}")
    print(f"Train MAE: {mean_absolute_error(Y_train, Y_train_pred)}")
    print(f"Test MAE: {mean_absolute_error(Y_test, Y_test_pred)}")
    print("Metrics logged successfully.")

    # Enregistrer le modèle avec un nom spécifique
    model_name = f"{args.regressor}_model.joblib"
    dump(predictor, model_name)
    print(f"Model saved as {model_name}")

    print("Training completed.")

if __name__ == "__main__":
    main()