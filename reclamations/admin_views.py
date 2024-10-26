# admin_views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Reclamation
import pandas as pd
import plotly.express as px
from plotly.offline import plot

@staff_member_required
def statistiques_admin(request):
    # Récupérer toutes les réclamations
    reclamations = Reclamation.objects.all().values()
    df = pd.DataFrame(reclamations)

    # Créer un graphique des réclamations par type
    if not df.empty:
        fig = px.histogram(df, x='type_reclamation', title='Réclamations par Type')
        graph = plot(fig, include_plotlyjs=False, output_type='div')
    else:
        graph = None

    return render(request, 'admin/statistiques.html', {'graph': graph})
