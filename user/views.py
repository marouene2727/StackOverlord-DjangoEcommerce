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
import face_recognition
import numpy as np
import base64
import io
from django.http import JsonResponse
import json
import logging

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
        # Vérifie d'abord les informations d'identification classiques
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

        # Vérifie si une image de visage a été soumise pour l'authentification
        if 'face_image' in request.FILES:
            face_image = request.FILES['face_image']
            user_profile = UserProfile.objects.filter(user__username=username).first()
            if user_profile and user_profile.face_encoding:
                # Comparer l'image soumise avec l'encodage enregistré
                face_encoding = get_face_encoding(face_image)
                if face_encoding is not None:
                    stored_encoding = np.frombuffer(user_profile.face_encoding, dtype=np.float64)
                    results = face_recognition.compare_faces([stored_encoding], face_encoding)
                    if results[0]:
                        login(request, user_profile.user)
                        return redirect('home')
                    else:
                        messages.error(request, "Échec de la reconnaissance faciale.")
                else:
                    messages.error(request, "Aucun visage détecté dans l'image.")
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
    user = request.user
    profile = user.userprofile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            # Générer une suggestion de bio si elle n'est pas fournie
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


logger = logging.getLogger(__name__)
def get_face_encoding(image):
    # Convertir l'image en RGB si elle ne l'est pas déjà
    if image.mode != "RGB":
        image = image.convert("RGB")
    image_np = np.array(image)
    face_encodings = face_recognition.face_encodings(image_np)
    return face_encodings[0] if face_encodings else None

def authenticate_face(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            image_data = data.get('image')

            if not image_data:
                return JsonResponse({'error': 'Aucune image fournie'}, status=400)

            # Vérifier si l'image contient le préfixe
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            else:
                return JsonResponse({'error': 'Données d\'image non valides'}, status=400)

            # Décode l'image de base64
            image_binary = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_binary))

            # Log des informations sur l'image
            logger.info(f"Mode de l'image : {image.mode}")
            logger.info(f"Taille de l'image : {image.size}")

            # Convertir l'image en RGB
            if image.mode != "RGB":
                logger.info(f"Conversion de l'image de {image.mode} à RGB")
                image = image.convert("RGB")

            # Vérifier le mode après conversion
            logger.info(f"Mode après conversion : {image.mode}")

            face_encoding = get_face_encoding(image)
            if face_encoding is None:
                return JsonResponse({'error': 'Aucun visage détecté'}, status=400)

            # Récupérer les encodages des utilisateurs enregistrés
            users_encodings = [(user.id, user.face_encoding) for user in User.objects.all()]

            # Comparer l'encodage de l'image de login à ceux des utilisateurs
            matches = face_recognition.compare_faces([encoding for _, encoding in users_encodings], face_encoding)

            if True in matches:
                matched_user_id = users_encodings[matches.index(True)][0]
                # Authentifier l'utilisateur (par exemple, en créant une session)
                return JsonResponse({'success': 'Reconnaissance faciale réussie', 'user_id': matched_user_id}, status=200)
            else:
                return JsonResponse({'error': 'Échec de la reconnaissance faciale'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON invalide'}, status=400)
        except Exception as e:
            logger.error(f"Erreur de traitement de l'image : {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

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


