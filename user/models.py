from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)  # Nouveau champ adresse
    gender = models.CharField(max_length=10, choices=[('Monsieur', 'Monsieur'), ('Madame', 'Madame')], blank=True)  # Nouveau champ genre
    birth_date = models.DateField(blank=True, null=True)  # Nouveau champ date de naissance

    def __str__(self):
        return f'{self.user.username} Profile'
