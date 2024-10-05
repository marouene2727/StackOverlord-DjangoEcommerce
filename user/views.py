from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('/admin/')  # Redirection vers le dashboard admin
                else:
                    return redirect('home')  # Redirection vers le tableau de bord utilisateur
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def home(request):
    return render(request, 'index.html')
@login_required
def shop(request):
    return render(request, 'shop.html')
@login_required
def notFound(request):
    return render(request, '404.html')
@login_required
def cart(request):
    return render(request, 'cart.html')
@login_required
def checkout(request):
    return render(request, 'chackout.html')
@login_required
def contact(request):
    return render(request, 'contact.html')
@login_required
def shopDetails(request):
    return render(request, 'shop-detail.html')
@login_required
def testimonial(request):
    return render(request, 'testimonial.html')
