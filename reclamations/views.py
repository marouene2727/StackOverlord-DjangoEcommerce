from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .forms import ReclamationForm
from django.contrib.auth.decorators import login_required
from .models import Reclamation

@login_required
def soumettre_reclamation(request):
    if request.method == 'POST':
        form = ReclamationForm(request.POST)
        if form.is_valid():
            reclamation = form.save(commit=False)
            reclamation.user = request.user
            reclamation.save()
            return redirect('liste_reclamations')
    else:
        form = ReclamationForm()
    return render(request, 'soumettre_reclamation.html', {'form': form})


@login_required
def liste_reclamations(request):
    reclamations = Reclamation.objects.filter(user=request.user)
    return render(request, 'liste_reclamations.html', {'reclamations': reclamations})
