from django.shortcuts import render, redirect
from .forms import ReclamationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reclamation
from better_profanity import profanity  # Importer la bibliothèque

# Charger les mots inappropriés (vous pouvez personnaliser les mots ici)
profanity.load_censor_words()

@login_required
def soumettre_reclamation(request):
    if request.method == 'POST':
        form = ReclamationForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            
            # Vérifier si la description contient des mots inappropriés
            if profanity.contains_profanity(description):
                messages.error(request, "La description contient des mots inappropriés. Veuillez reformuler.")
                return render(request, 'soumettre_reclamation.html', {'form': form})
            else:
                reclamation = form.save(commit=False)
                reclamation.user = request.user
                reclamation.save()
                messages.success(request, "Réclamation soumise avec succès.")
                return redirect('liste_reclamations')
    else:
        form = ReclamationForm()
    
    return render(request, 'soumettre_reclamation.html', {'form': form})

@login_required
def liste_reclamations(request):
    reclamations = Reclamation.objects.filter(user=request.user)
    return render(request, 'liste_reclamations.html', {'reclamations': reclamations})
