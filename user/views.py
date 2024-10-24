from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm
from django.http import HttpResponse
from django.core.mail import send_mail
import ssl
from .forms import UserUpdateForm
from django.contrib import messages
from .forms import UserProfileForm
from django.views.generic.edit import UpdateView
from .models import UserProfile 
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class CustomPasswordResetView(PasswordResetView):
    def post(self, request, *args, **kwargs):
        print("Tentative d'envoi d'e-mail...")
        return super().post(request, *args, **kwargs)

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


def send_test_email(request):
    ssl._create_default_https_context = ssl._create_unverified_context

    send_mail(
        'Sujet de test',
        'Voici le contenu du test d\'envoi.',
        'rahmaaslimii83@gmail.com',
        ['rahmaaslimii83@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse("Email envoyé !")

@login_required
def user_profile(request):
    """ Affiche les informations du profil utilisateur """
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Créer un profil si l'utilisateur n'en a pas
        profile = UserProfile.objects.create(user=request.user)
    
    # save_profile_picture(profile)
    return render(request, 'user_profile.html', {'profile': profile})

@login_required
def update_user_profile(request):
    """ Met à jour les informations du profil utilisateur """
    user = request.user
    profile = user.userprofile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            # Generate bio suggestion if bio is not provided
            if not profile_form.cleaned_data['bio']:
                profile.bio = generate_bio_suggestion(user.username, profile.birth_date)
            
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('user_profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'profile_update.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def generate_bio_suggestion(username, birth_date):
    # Calculate age
    if birth_date:
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    else:
        age = None
    
    # Generate bio based on username and age
    if age:
        return f"{username} is {age} years old and loves exploring new products!"
    else:
        return f"{username} is an enthusiastic user with diverse interests."
def generate_avatar(username):
    # Crée une image de base
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))

    # Ajoute un dessin sur l'image
    d = ImageDraw.Draw(img)
    
    # Par exemple, ajouter la première lettre du nom d'utilisateur
    font = ImageFont.load_default()
    d.text((10, 10), username[0].upper(), fill=(255, 255, 0), font=font)

    # Enregistre l'image générée dans le répertoire des avatars
    img_path = f"media/avatars/{username}.png"
    img.save(img_path)

    return img_path

# def save_profile_picture(request):
#     user_profile = request.user.userprofile
    
#     # Si l'utilisateur n'a pas d'avatar, on le génère automatiquement
#     if not user_profile.profile_image:
#         user_profile.profile_image = user_profile.generate_avatar()
    
#     # Sauvegarder le profil après mise à jour
#     user_profile.save()



      
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


