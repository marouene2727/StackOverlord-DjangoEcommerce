import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('corpus')


from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Review

from django.db.models import Count, Case, When, IntegerField



from textblob import TextBlob





from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
#

@login_required
def home(request):
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
    product = get_object_or_404(Product, name=product_name)
    reviews = product.reviews.all()
    
    sentiment_counts = reviews.aggregate(
        positive=Count(Case(When(sentiment='positive', then=1))),
        negative=Count(Case(When(sentiment='negative', then=1))),
        neutral=Count(Case(When(sentiment='neutral', then=1)))
    )
    
    total_reviews = sum(sentiment_counts.values())
    satisfaction_rate = (sentiment_counts['positive'] / total_reviews * 100) if total_reviews > 0 else 0
    
    context = {
        'product': product,
        'categories': Category.objects.all(),
        'products': Product.objects.all(),
        'related_products': Product.objects.filter(category=product.category).exclude(id=product.id),
        'reviews': reviews,
        'sentiment_counts': sentiment_counts,
        'satisfaction_rate': round(satisfaction_rate, 2)
    }
    return render(request, 'shop-detail.html', context)





@login_required
def add_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        sentiment = analyze_sentiment(comment)
        Review.objects.create(product=product, comment=comment, rating=rating, sentiment=sentiment)
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