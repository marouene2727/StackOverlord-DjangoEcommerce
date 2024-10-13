import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

import logging

from django.db.models import Count




from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Review

from django.db.models import Count, Case, When, IntegerField

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.db.models import Q



from textblob import TextBlob





from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import requests
#

logger = logging.getLogger(__name__)


@login_required
def home(request):
    print("salut")
    return render(request, 'index.html')

@login_required
def shop(request):
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id
    }
    return render(request, 'shop.html', context)


@login_required
def shopDetails(request, product_name):
    product = get_object_or_404(Product.objects.annotate(
        user_review_count=Count('reviews', filter=Q(reviews__user=request.user))
    ), name=product_name)

    reviews = Review.objects.filter(product=product).order_by('-created_at')

    sentiment_counts = {
        'positive': reviews.filter(sentiment='positive').count(),
        'neutral': reviews.filter(sentiment='neutral').count(),
        'negative': reviews.filter(sentiment='negative').count(),
    }
    total_reviews = sum(sentiment_counts.values())
    satisfaction_rate = (sentiment_counts['positive'] / total_reviews * 100) if total_reviews > 0 else 0

    context = {
        'product': product,
        'reviews': reviews,
        'sentiment_counts': sentiment_counts,
        'satisfaction_rate': round(satisfaction_rate, 2)
    }
    return render(request, 'shop-detail.html', context)






@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_review_count = Review.objects.filter(product=product, user=request.user).count()

    if request.method == 'POST' and (user_review_count < 3 or request.user.is_superuser):
        comment = filter_profanity(request.POST.get('comment'))
        rating = request.POST.get('rating')
        Review.objects.create(product=product, user=request.user, comment=comment, rating=rating)
        return redirect('shopDetails', product_name=product.name)

    return redirect('shopDetails', product_name=product.name)











def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    tokens = word_tokenize(text.lower(), language='french')
    stop_words = set(stopwords.words('french'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    sentiment = sia.polarity_scores(' '.join(filtered_tokens))
    
    if sentiment['compound'] > 0.05:
        return 'positive'
    elif sentiment['compound'] < -0.05:
        return 'negative'
    else:
        return 'neutral'
    






@login_required
@require_POST
def update_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    data = json.loads(request.body)
    review.comment = data['comment']
    review.save()
    return JsonResponse({
        'success': True,
        'comment': review.comment,
        'updated_at': review.updated_at.strftime('%B %d, %Y')
    })


@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return JsonResponse({'success': True, 'message': 'Review supprimée avec succès'})




import requests

def filter_profanity(text):
    api_url = f"https://www.purgomalum.com/service/json?text={text}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()['result']
    return text




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
def testimonial(request):
    return render(request, 'testimonial.html')