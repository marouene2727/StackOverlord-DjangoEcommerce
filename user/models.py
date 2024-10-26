from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)  # Nouveau champ adresse
    gender = models.CharField(max_length=10, choices=[('Monsieur', 'Monsieur'), ('Madame', 'Madame')], blank=True)  # Nouveau champ genre
    birth_date = models.DateField(blank=True, null=True)  # Nouveau champ date de naissance
    face_encoding = models.BinaryField(null=True, blank=True)  # Champ pour stocker l'encodage du visage
    
    def __str__(self):
        return f'{self.user.username} Profile'
        
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
    