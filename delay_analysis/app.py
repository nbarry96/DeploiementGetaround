############################
# Import des Bibliothèques #
############################

import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import math

##############
# Fonctions  #
##############

# Transformation de la colonne state en fonction du delais de la restitution en minutes.
def clean_state(row):
    state = 'Unknown'
    if row['state'] == 'ended':
        if row['delay_at_checkout_in_minutes'] <= 0:
            state = "On time checkout"
        elif row['delay_at_checkout_in_minutes'] > 0:
            state = "Late checkout"
    if row['state'] == 'canceled':
        state = "Canceled"
    return state

# Fonction pour extraire le retard de la location précédente
def extract_previous_rental_delay(row, dataframe):
    previous_delay = np.nan
    if not pd.isnull(row['previous_ended_rental_id']):
        prev_rental_id = row['previous_ended_rental_id']
        matching_delays = dataframe[dataframe['rental_id'] == prev_rental_id]['delay_at_checkout_in_minutes'].values
        if len(matching_delays) > 0:
            previous_delay = matching_delays[0]
    return previous_delay


# Fonction pour déterminer l'impact du retard de la location précédente
def determine_impact_of_previous_rental_delay(row):
    impact = 'No previous rental filled out'
    if not math.isnan(row['checkin_delay']):
        if row['checkin_delay'] > 0:
            if row['state'] == 'Canceled':
                impact = 'Cancelation'
            else:
                impact = 'Late checkin'
        else:
            impact = 'No impact'
    return impact

def calculate_statistics(data):
    # Nombre total de locations
    total_locations = data.shape[0]

    # Nombre total de voitures
    total_cars = data['car_id'].nunique()

    # Nombre d'annulations
    canceled_bookings = data[data['state'] == 'Canceled'].shape[0]
    cancellation_percentage = (canceled_bookings / total_locations) * 100

    # Nombre de 'connect' check-ins
    connect_checkins = data[data['checkin_type'] == 'connect'].shape[0]
    mobile_checkins = data[data['checkin_type'] == 'mobile'].shape[0]
    connect_percentage = (connect_checkins / total_locations) * 100
    mobile_percentage = (mobile_checkins / total_locations) * 100

    # Statistiques des temps entre les locations consécutives
    time_delta_stats = data['time_delta_with_previous_rental_in_minutes'].describe()
    max_time_delta = time_delta_stats['max']
    mean_time_delta = time_delta_stats['mean']

    # Tri du DataFrame par car_id et rental_id
    df_sorted = data.sort_values(by=['car_id', 'rental_id'])

    # Calcul du pourcentage de locations consécutives
    df_sorted['is_consecutive'] = df_sorted['time_delta_with_previous_rental_in_minutes'].notna()
    consecutive_locations = df_sorted['is_consecutive'].sum()
    consecutive_percentage = (consecutive_locations / total_locations) * 100

    return {
        "total_locations": total_locations,
        "total_cars": total_cars,
        "canceled_bookings": canceled_bookings,
        "cancellation_percentage": cancellation_percentage,
        "connect_checkins": connect_checkins,
        "connect_percentage": connect_percentage,
        "mobile_checkins": mobile_checkins,
        "mobile_percentage": mobile_percentage,
        "max_time_delta": max_time_delta,
        "mean_time_delta": mean_time_delta,
        "consecutive_locations": consecutive_locations,
        "consecutive_percentage": consecutive_percentage
    }

# Fonction pour calculer les pourcentages de retard
def calculate_delay_percentages(data):
    total_rentals = len(data)
    less_than_30m = len(data[(data['delay_at_checkout_in_minutes'] > 0) & (data['delay_at_checkout_in_minutes'] <= 30)])
    between_30m_1h = len(data[(data['delay_at_checkout_in_minutes'] > 30) & (data['delay_at_checkout_in_minutes'] <= 60)])
    more_than_1h = len(data[data['delay_at_checkout_in_minutes'] > 60])


    percent_less_than_30m = (less_than_30m / total_rentals) * 100
    percent_between_30m_1h = (between_30m_1h / total_rentals) * 100
    percent_more_than_1h = (more_than_1h / total_rentals) * 100

    return {
        "percent_less_than_30m": percent_less_than_30m,
        "percent_between_30m_1h": percent_between_30m_1h,
        "percent_more_than_1h": percent_more_than_1h
    }

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def keep_only_ended_rentals(dataframe):
    return dataframe[(dataframe['state'] == 'On time checkout') | (dataframe['state'] == 'Late checkout')]

def keep_only_late_checkins_canceled(dataframe):
    return dataframe[(dataframe['checkin_delay'] > 0) & (dataframe['state'] == 'Canceled')]

def apply_threshold(dataframe, threshold, scope):
    if scope == 'All':
        rows_to_drop_df = dataframe[dataframe['time_delta_with_previous_rental_in_minutes'] < threshold]
    elif scope == 'Connect':
        rows_to_drop_df = dataframe[(dataframe['time_delta_with_previous_rental_in_minutes'] < threshold) & (dataframe['checkin_type'] == 'connect')]
    elif scope == 'mobile':
        rows_to_drop_df = dataframe[(dataframe['time_delta_with_previous_rental_in_minutes'] < threshold) & (dataframe['checkin_type'] == 'mobile')]
    else:
        raise ValueError("Scope must be 'All', 'Connect', or 'mobile'")

    nb_ended_rentals_dropped = len(keep_only_ended_rentals(rows_to_drop_df))
    nb_late_checkins_cancelations_dropped = len(keep_only_late_checkins_canceled(rows_to_drop_df))
    output = (
        dataframe.drop(rows_to_drop_df.index),
        nb_ended_rentals_dropped,
        nb_late_checkins_cancelations_dropped
    )

    return output



############################################
### Configuration de mon tableau de bord ###
############################################

st.set_page_config(
    page_title="Getaround",
    page_icon="🚗",
    layout="wide"
)

###################
### Application ###
###################
st.title("Analyse des données de Getaround 🚗")

st.markdown("""
   GetAround est une plateforme similaire à Airbnb, mais dédiée à la location de voitures. Elle permet à tout le monde de louer des véhicules pour une durée allant de quelques heures à quelques jours. Fondée en 2009, l'entreprise a rapidement évolué. En 2019, elle compte plus de 5 millions d'utilisateurs et environ 20 000 voitures disponibles à travers le monde.
""")

st.subheader("**Contexte** ℹ️")

st.markdown("""
Lors de la location d'une voiture sur GetAround, les utilisateurs doivent suivre un processus de check-in au début de la location et un processus de check-out à la fin de la location afin de :

- Évaluer l’état de la voiture et signaler les dommages préexistants ou survenus pendant la location.
- Comparer les niveaux de carburant.
- Mesurer la distance parcourue.

Les check-in et check-out peuvent se faire via trois types de flux distincts :

- **Contrat de location mobile sur applications natives** : Le conducteur et le propriétaire se rencontrent et signent le contrat de location sur le smartphone du propriétaire.
- **Connect** : Le conducteur ne rencontre pas le propriétaire et ouvre la voiture avec son smartphone. Contrat papier (négligeable).
""")

st.subheader("**Projet** 🚧")

st.markdown("""
Lorsqu'ils utilisent Getaround, les conducteurs réservent des voitures pour une période spécifique, allant d'une heure à quelques jours. Ils sont censés ramener la voiture à l'heure prévue, mais il arrive parfois que les conducteurs soient en retard au retour.

Les retours tardifs peuvent créer de grandes frictions pour le conducteur suivant si la voiture doit être louée de nouveau le même jour. Le service client reçoit souvent des plaintes d'utilisateurs insatisfaits qui ont dû attendre que la voiture revienne de la location précédente, ou pire encore, qui ont dû annuler leur location car la voiture n'était pas restituée à temps.
""")

st.subheader("**Objectifs** 🎯")

st.markdown("""
Une stratégie pour résoudre ce problème serait de mettre en place un délai minimum entre deux locations, empêchant ainsi l'affichage de voitures dans les résultats de recherche si les heures d'arrivée ou de départ demandées se chevauchent trop avec une réservation existante. Cependant, cette solution pourrait impacter à la fois GetAround et les revenus des propriétaires de voitures.

L'objectif de cette analyse est donc d'examiner certains éléments pour aider à prendre cette décision :
- Le seuil à appliquer, déterminant la durée minimale entre deux locations.
- La portée de ce seuil, déterminant si toutes les voitures doivent être soumises à cette restriction ou seulement celles qui utilisent le service 'Connect'.
""")

###### Chargement des données brutes

DATA_URL = ('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx')

@st.cache_data
def load_data(nrows=None):
    data = pd.read_excel(DATA_URL, nrows=nrows)
    return data

# Affiche un texte indiquant que les données sont en cours de chargement
data_load_state = st.text('Chargement des données...')
raw_data = load_data() # Charger les données sans limite de lignes
data_load_state.text("Données chargées avec succès!")

# Affichage conditionnel des données brutes
if st.checkbox('Afficher les données brutes'):
    st.subheader('Données brutes')
    st.write(raw_data)

###### Prétraitement des données
prep_data = raw_data.copy()

# Modification « State » pour ajouter des informations indiquant si la restitution est à l'heure ou en retard 
prep_data['state'] = prep_data.apply(clean_state, axis=1)

# Ajout d'une colonne qui marque le délai de restitution de la location précédente
prep_data['previous_rental_checkout_delay'] = prep_data.apply(extract_previous_rental_delay, args=[prep_data], axis=1)


# Ajout d'une colonne qui marque le délais de délai d'enregistrement 
prep_data['checkin_delay'] = prep_data['previous_rental_checkout_delay'] - prep_data['time_delta_with_previous_rental_in_minutes']
prep_data['checkin_delay'] = prep_data['checkin_delay'].apply(lambda x: 0 if x < 0 else x)
    
# Ajout d'une colonne qui défini l'impact du délai de la location précédente 
prep_data['impact_of_previous_rental_delay'] = prep_data.apply(determine_impact_of_previous_rental_delay, axis=1)

# Affichage conditionnel des données traitées
if st.checkbox('Afficher les données traitées'):
    st.subheader('Données traitées')
    st.write(prep_data)

# Afficher la description des données modifiées 
st.write("Remarque : Toutes les analyses ci-dessous sont effectuées sur des données traitées.")
st.write("- Modification de la colonne 'state' pour indiquer si la restitution a été effectuée à l'heure ou en retard.")
st.write("- Ajout de la colonne 'previous_rental_checkout_delay' pour obtenir des informations sur le délai de restitution de la location précédente")
st.write("- Ajout de la colonne 'checkin_delay' pour obtenir des informations sur le délai d'enregistrement.")
st.write("- Ajout de la colonne 'impact_of_previous_rental_delay' pour obtenir des informations sur l'impact du délai de la location précédente.")

###### Statistiques des données 
stats = calculate_statistics(prep_data)
# Extraire les valeurs des statistiques
total_locations = stats["total_locations"]
total_cars = stats["total_cars"]
cancellation_percentage = stats["cancellation_percentage"]
connect_checkins = stats["connect_checkins"]
connect_percentage = stats["connect_percentage"]
max_time_delta = stats["max_time_delta"]
mean_time_delta = stats["mean_time_delta"]
consecutive_locations = stats["consecutive_locations"]
consecutive_percentage = stats["consecutive_percentage"]

st.header('Statistiques sur les locations de voitures')

# Diviser la section en quatre colonnes
main_metrics_cols = st.columns(3)

with main_metrics_cols[0]:
    st.metric(label="Nombre de locations 🚗", value=stats['total_locations'])
    st.metric(label="Nombre de voitures 🚙", value=stats['total_cars'])

with main_metrics_cols[1]:
    st.metric(label="Taux d'annulation ❌", value=f"{stats['cancellation_percentage']:.2f}%")
    st.metric(label="Taux de Locations consécutives 🔄", value=f"{stats['consecutive_percentage']:.2f}%")
    

with main_metrics_cols[2]:
    st.metric(label="Temps maximal entre locations ⏰", value=f"{int(stats['max_time_delta'])} min")
    st.metric(label="Temps moyen entre locations ⏳", value=f"{int(stats['mean_time_delta'])} min")


###### Visualisations des données
st.header('Visualisations des données')

# Répartition des statuts de locations
info_cols = st.columns([35, 10, 35])
with info_cols[0]:
    fig1 = px.pie(
    prep_data, 
    names="state", 
    color="state", 
    height=500, 
    color_discrete_map={
        'On time checkout': 'navy',  
        'Late checkout': 'FFC107',  
        'Canceled': 'red',  
        'Unknown': 'gray'  
    },
    category_orders={"state": ["On time checkout", 'Late checkout', 'Canceled', 'Unknown']},
    title="<b>Statut des locations</b>")
    st.plotly_chart(fig1)



# Création d'un diagramme à barres pour les taux de location 'connect' et 'mobile'
checkin_data = pd.DataFrame({
    'Type de check-in': ['Connect', 'Mobile'],
    'Pourcentage': [stats['connect_percentage'], stats['mobile_percentage']]
})
checkin_data['Pourcentage'] = checkin_data['Pourcentage'].round(decimals=0)  

with info_cols[2]:
    fig2 = px.bar(checkin_data, x='Type de check-in', y='Pourcentage', title='Taux de locations par type de check-in',
                  labels={'Pourcentage': 'Pourcentage (%)', 'Type de check-in': 'Type de check-in'},
                  text='Pourcentage', height=400, color='Type de check-in',
                  color_discrete_map={'Connect': 'orange', 'Mobile': 'navy'})
    st.plotly_chart(fig2)

# Visualisation des données de Checkout à l'aide d'un diagramme à bar
total_rentals = len(prep_data)
delayed_rentals = prep_data[prep_data['delay_at_checkout_in_minutes'] > 0]
on_time_rentals = prep_data[prep_data['delay_at_checkout_in_minutes'] <= 0]
nan_rentals = prep_data[prep_data['delay_at_checkout_in_minutes'].isnull()]

delayed_percent = (len(delayed_rentals) / total_rentals) * 100
on_time_percent = (len(on_time_rentals) / total_rentals) * 100
nan_percent = (len(nan_rentals) / total_rentals) * 100

data_bar_chart = pd.DataFrame({
    'Status': ['En retard', 'À l\'heure', 'Non renseigné'],
    'Pourcentage': [delayed_percent, on_time_percent, nan_percent]
})
data_bar_chart['Pourcentage'] = data_bar_chart['Pourcentage'].round(decimals=0)

info_cols2 = st.columns([35, 10, 35])
with info_cols2[0]:
    fig3 = px.bar(data_bar_chart, x='Status', y='Pourcentage', text='Pourcentage',
                title='Données relatives aux Checkout',
                labels={'Status': 'Statut', 'Pourcentage': 'Pourcentage (%)'},
                color='Status', color_discrete_map={'En retard': 'red', 'À l\'heure': 'navy', 'Non renseigné': 'gray'})
    st.plotly_chart(fig3)

# Statisqtiques sur les retards 
stats_late = calculate_delay_percentages(prep_data)
with info_cols2[2]:
    st.write("**Statistiques des retards**")
    st.metric(label="Retard moins de 30 minutes", value=f"{round(stats_late['percent_less_than_30m'])}%", delta="de locations avec un retard de moins de 30 minutes", delta_color='inverse')
    st.metric(label="Retard entre 30 minutes et 1 heure", value=f"{round(stats_late['percent_between_30m_1h'])}%", delta="de locations avec un retard entre 30 minutes et 1 heure", delta_color='inverse')
    st.metric(label="Retard plus d\'1 heure", value=f"{round(stats_late['percent_more_than_1h'])}%", delta="de locations avec un retard de plus de 1 heure", delta_color='inverse')


# Visualisation des Impacts des retards sur le prochain Chekin
st.header('Impacts des retards sur le prochain Checkin')

previous_rental_checkout_delay_df = prep_data[prep_data['previous_rental_checkout_delay'] > 0] # On prend que les checkout de location précédente supérieur à zéro

info_cols3 = st.columns([35, 10, 35])
with info_cols3[0]:
    impacts_pie = px.pie(
        previous_rental_checkout_delay_df, 
        names="impact_of_previous_rental_delay", 
        color="impact_of_previous_rental_delay", 
        height=500, 
        color_discrete_map={
            'No impact': 'navy',  # Changer ici si 'colors' est défini ailleurs
            'Late checkin': 'FFC107',  # Changer ici si 'colors' est défini ailleurs
            'Cancelation': 'red',  # Changer ici si 'colors' est défini ailleurs
            'No previous rental filled out': 'gray'  # Changer ici si 'colors' est défini ailleurs
        },
        category_orders={"impact_of_previous_rental_delay": ['Aucun impact', 'Retard Chekin', 'Annulation', 'Aucune location précédente renseignée']},
        title="<b>Impacts des retards sur le prochain Checkin</b>"
    )
    st.plotly_chart(impacts_pie)

with info_cols3[2]:
    gif_pathh = load_lottieurl('https://lottie.host/837dfd9a-7345-46a5-ad2e-32853828f13f/pTRDKDo3dK.json')
    st_lottie(gif_pathh, width=500)
   
###### Formulaire de saisie de simulation
with st.form(key='simulation_form'):
    simulation_form_cols = st.columns([20, 20, 20, 15, 25])
    with simulation_form_cols[0]:
        simulation_threshold = st.number_input(label='Seuil (minutes)', min_value=15, step=15)
    with simulation_form_cols[1]:
        simulation_scope = st.radio('Portée', ['All', 'Connect', 'mobile'], key=3)
    submit = st.form_submit_button(label='Exécutez une Simulation 🚀')

if submit:
    with_threshold_df, nb_ended_rentals_lost, nb_late_checkins_cancelations_avoided = apply_threshold(prep_data, simulation_threshold, simulation_scope)
    previous_rental_delay_with_threshold_df = with_threshold_df[with_threshold_df['previous_rental_checkout_delay'] > 0]
    
    # Influence sur les indicateurs commerciaux
    nb_ended_rentals = len(keep_only_ended_rentals(prep_data))
    nb_late_checkins_cancelations = len(keep_only_late_checkins_canceled(prep_data))

    gif_path = load_lottieurl('https://lottie.host/06ee9963-f040-483f-a837-37977cc82648/Mh7m7qu8qV.json')

    with simulation_form_cols[2]:
        st_lottie(gif_path, width=100)
    
    with simulation_form_cols[3]:
        st.metric(
            label = "", 
            value=f"{round(nb_ended_rentals_lost / nb_ended_rentals * 100, 1)}%", 
            delta = "Perte de Revenue",
            delta_color = 'inverse'
            )
    with simulation_form_cols[4]:
        st.metric(
            label = "", 
            value=f"{round(nb_late_checkins_cancelations_avoided / nb_late_checkins_cancelations * 100)}%",
            delta = "**Annulations évitées grâce à la gestion des Checkouts tardifs**",
            delta_color = 'normal'
        )

    # Visualisations
    st.markdown("**Impacts des retards sur le prochain Checkin - Evolution de l'Impacts des retards**")
    if len(previous_rental_delay_with_threshold_df['impact_of_previous_rental_delay']) == 0:
        late_checkouts_impact_evolution_cols = st.columns([30, 10, 5, 25, 30])
        with late_checkouts_impact_evolution_cols[3]:
            st.markdown("### _No more rentals consecutive to a delayed one_")
    else:
        late_checkouts_impact_evolution_cols = st.columns([35, 20, 35])
        with late_checkouts_impact_evolution_cols[2]:
            impacts_pie_with_threshold = px.pie(
                previous_rental_delay_with_threshold_df, 
                names = "impact_of_previous_rental_delay", color = "impact_of_previous_rental_delay", 
                height = 500, 
                color_discrete_map={
                    'No impact':'navy', 
                    'Late checkin': 'FFC107', 
                    'Cancelation': 'red',
                    'No previous rental filled out': 'gray'
                    },
                category_orders={"impact_of_previous_rental_delay": ['No impact', 'Late checkin', 'Cancelation', 'No previous rental filled out']},
                title = "<b>Avec seuil</b>")
            st.plotly_chart(impacts_pie_with_threshold)
    with late_checkouts_impact_evolution_cols[0]:
        impacts_pie_without_threshold = impacts_pie
        impacts_pie_without_threshold.update_layout(title = "<b>Sans seuil</b>")
        st.plotly_chart(impacts_pie_without_threshold)
    with late_checkouts_impact_evolution_cols[1]:
        st_lottie(gif_path, height = 200)
            







