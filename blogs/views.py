from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm
from django.http import HttpResponse

from .utils import analyze_sentiment, summarize_article  # Ajustez le chemin selon la structure de votre projet

from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Comment
from .forms import ArticleForm, CommentForm
from django.contrib.auth.decorators import login_required
from .models import Blog

import json
import numpy as np
from django.http import JsonResponse
from vosk import Model, KaldiRecognizer
import wave
from .comment_moderation import predict_comment  # Importer la fonction de prédiction

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


# Article CRUD

@login_required
def article_list(request):
    tab = request.GET.get('tab', 'all')  # Récupère l'onglet sélectionné, par défaut 'all'
    
    if tab == 'user':
        articles = Article.objects.filter(author=request.user)
    elif tab == 'others':
        articles = Article.objects.exclude(author=request.user)
    else:
        articles = Article.objects.all()
    
    return render(request, 'articles/article_list.html', {'articles': articles, 'tab': tab})

@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.all()
    sentiment_scores = [(comment.created_at.strftime("%Y-%m-%d %H:%M"), comment.sentiment_score) for comment in comments]

    # Générer le résumé de l'article
    try:
        summary = summarize_article(article.content)
    except Exception as e:
        summary = "Erreur lors de la génération du résumé."

    form = CommentForm()  # Créer un formulaire vide pour ajouter un commentaire
    return render(request, 'articles/article_detail.html', {
        'article': article,
        'comments': comments,
        'form': form,
        'summary': summary,  # Passer le résumé au template
    })
@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('article_list')
        else:
            # Gérer les erreurs de validation ici si nécessaire
            error = form.errors.as_text()  # Récupérer les erreurs
    else:
        form = ArticleForm()
    
    blogs = Blog.objects.all()
    return render(request, 'articles/article_form.html', {'form': form, 'blogs': blogs})

@login_required
def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article_list')  # Redirige vers la liste des articles
    else:
        form = ArticleForm(instance=article)

    blogs = Blog.objects.all()  # Récupérer tous les blogs
    return render(request, 'articles/article_form.html', {'form': form, 'blogs': blogs, 'article': article})

@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    
    # Vérifie si l'utilisateur est l'auteur de l'article
    if request.user != article.author:
        return redirect('article_detail', pk=article.pk)
    
    article.delete()
    return redirect('article_list')

# Comment CRUD

@login_required
def comment_create(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_content = form.cleaned_data['content']
            prediction = predict_comment(comment_content)
            sentiment_label, sentiment_score = analyze_sentiment(comment_content)

            print(f"Commentaire : {comment_content}")
            print(f"Label de sentiment : {sentiment_label}, Score : {sentiment_score}, Prédiction : {prediction}")

            # Logique de modération
            if sentiment_label == 'NEGATIVE' and sentiment_score > 0.75:
                return render(request, 'articles/article_detail.html', {
                    'article': article,
                    'comments': article.comments.all(),
                    'form': form,
                    'error': 'Commentaire modéré en raison d\'un contenu négatif.'
                })

            if prediction == 0:  # Si votre fonction de prédiction retourne 1 pour modéré
                return render(request, 'articles/article_detail.html', {
                    'article': article,
                    'comments': article.comments.all(),
                    'form': form,
                    'error': 'Commentaire modéré.'
                })

            # Si aucune condition de modération n'est rencontrée, enregistrez le commentaire
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.sentiment_label = sentiment_label
            comment.sentiment_score = sentiment_score
            comment.save()

            return redirect('article_detail', pk=article.pk)

    else:
        form = CommentForm()

    # Filtrer les commentaires pour n'afficher que ceux jugés négatifs
    negative_comments = [comment for comment in article.comments.all() if comment.sentiment_label == 'NEGATIVE']

    return render(request, 'articles/article_detail.html', {
        'article': article,
        'comments': article.comments.all(),  # Tous les commentaires pour le contexte
        'negative_comments': negative_comments,  # Négatifs uniquement pour l'affichage
        'form': form
    })


@login_required
def comment_update(request, article_pk, comment_pk):
    article = get_object_or_404(Article, pk=article_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)

    if request.user != comment.author:
        return redirect('article_detail', pk=article.pk)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('article_detail', pk=article.pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'comments/comment_form.html', {'form': form, 'article': article, 'comment': comment})
@login_required
def comment_delete(request, article_pk, comment_pk):
    article = get_object_or_404(Article, pk=article_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)

    # Vérifie si l'utilisateur est l'auteur du commentaire
    if request.user != comment.author:
        return redirect('article_detail', pk=article.pk)

    comment.delete()
    return redirect('article_detail', pk=article.pk)

@login_required
def transcribe_audio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            audio_data = np.array(data['audio'], dtype=np.int16)

            if audio_data.size == 0:
                return JsonResponse({'error': 'No audio data provided'}, status=400)

            print(f'Received audio data size: {audio_data.size}')  # Debugging

            # Vérification de la taille du tableau audio
            if audio_data.size < 16000:
                return JsonResponse({'error': 'Audio data too short'}, status=400)

            model = Model("/Users/a123/Documents/vosk-model-fr-0.22")
            recognizer = KaldiRecognizer(model, 16000)

            # Enregistrement dans un fichier WAV
            with wave.open('temp.wav', 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_data.tobytes())

            results = []
            
            with wave.open('temp.wav', 'rb') as wf:
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        results.append(result)
                    else:
                        result = json.loads(recognizer.PartialResult())
                        results.append(result)

            final_result = json.loads(recognizer.FinalResult())
            results.append(final_result)

            # Créer la transcription finale
            transcript = " ".join([result['text'] for result in results if 'text' in result])
            return JsonResponse({'transcript': transcript})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def test_comment_analysis(request):
    comment_test = "Je déteste ce produit, il m'a causé des irritations"
    label, score = analyze_sentiment(comment_test)
    
    response_content = f"Commentaire: {comment_test}<br>Label: {label}<br>Score: {score:.2f}"
    return HttpResponse(response_content)




# views.py
@login_required
def sentiment_analysis_view(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    comments = article.comments.all()

    # Calculer le pourcentage de chaque sentiment
    sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
    total_comments = len(comments)

    for comment in comments:
        sentiment_counts[comment.sentiment_label] += 1

    # Calculer les pourcentages
    sentiment_percentages = {sentiment: (count / total_comments * 100) if total_comments > 0 else 0 
                             for sentiment, count in sentiment_counts.items()}

    return render(request, 'articles/sentiment_analysis.html', {
        'article': article,
        'sentiment_percentages': sentiment_percentages,
    })


