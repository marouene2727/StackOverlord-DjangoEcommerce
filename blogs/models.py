from django.db import models
from django.contrib.auth.models import User

class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    sujet = models.TextField()
    type = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Article(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)  # Nouveau champ pour l'image

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Relation avec l'utilisateur
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    moderated = models.BooleanField(default=False)  # Nouveau champ pour indiquer si le commentaire a été modéré
    sentiment_label = models.CharField(max_length=10, default='NEUTRAL')  # 'POSITIVE', 'NEGATIVE'
    sentiment_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"Comment by {self.author} on {self.article}"
