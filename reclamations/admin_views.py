# admin_views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Reclamation
import pandas as pd
import plotly.express as px
from plotly.offline import plot
from sklearn.linear_model import LinearRegression
import numpy as np

@staff_member_required
def statistiques_admin(request):
    # Récupérer toutes les réclamations
    reclamations = Reclamation.objects.all().values()
    df = pd.DataFrame(reclamations)

    # Créer un graphique des réclamations par type
    if not df.empty:
        # Graphique des réclamations par type
        fig_current = px.histogram(df, x='type_reclamation', title='Réclamations par Type')
        current_graph = plot(fig_current, include_plotlyjs=False, output_type='div')

        # Préparation des données pour le modèle de prévision
        df['date_creation'] = pd.to_datetime(df['date_creation'])  # Convertir les dates en datetime
        daily_counts = df.groupby(['date_creation', 'type_reclamation']).size().reset_index(name='counts')  # Compter par jour et type

        # Préparer les caractéristiques (X) et la cible (y) pour le modèle
        X = np.array(range(len(daily_counts))).reshape(-1, 1)  # Indices comme caractéristiques
        y = daily_counts['counts'].values  # Compte des réclamations comme cible

        # Créer un modèle de régression linéaire pour chaque type de réclamation
        types = daily_counts['type_reclamation'].unique()
        predictions_list = []

        for type_reclamation in types:
            type_data = daily_counts[daily_counts['type_reclamation'] == type_reclamation]
            X_type = np.array(range(len(type_data))).reshape(-1, 1)
            y_type = type_data['counts'].values

            # Entraîner le modèle
            model = LinearRegression()
            model.fit(X_type, y_type)

            # Prévoir pour les 7 jours suivants
            future_days = np.array(range(len(type_data), len(type_data) + 7)).reshape(-1, 1)
            predictions = model.predict(future_days)

            # Créer un DataFrame pour les prévisions
            future_dates = pd.date_range(start=type_data['date_creation'].max() + pd.Timedelta(days=1), periods=7)
            prediction_df = pd.DataFrame({'date': future_dates, 'predicted_counts': predictions, 'type_reclamation': type_reclamation})
            predictions_list.append(prediction_df)

        # Concaténer les prédictions
        final_predictions = pd.concat(predictions_list)

        # Créer un graphique des prévisions
        fig_prediction = px.line(final_predictions, x='date', y='predicted_counts', color='type_reclamation',
                                 title='Prédictions des Réclamations Futures par Type',
                                 labels={'predicted_counts': 'Nombre de Réclamations', 'date': 'Date'},
                                 markers=True)

        # Personnaliser le layout pour plus de clarté
        fig_prediction.update_layout(yaxis_title='Nombre de Réclamations', xaxis_title='Date',
                                     template='plotly_white',  # Utiliser un thème plus clair
                                     xaxis=dict(showgrid=False),  # Masquer la grille sur l'axe des x
                                     yaxis=dict(showgrid=True))  # Afficher la grille sur l'axe des y

        prediction_graph = plot(fig_prediction, include_plotlyjs=False, output_type='div')
    else:
        current_graph = None
        prediction_graph = None

    # Rendre le template avec les graphiques
    return render(request, 'admin/statistiques.html', {'current_graph': current_graph, 'prediction_graph': prediction_graph})
