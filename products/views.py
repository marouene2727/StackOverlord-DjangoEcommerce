import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Case, When, IntegerField
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Order, OrderItem, Product, Category, Review, Cart, CartItem
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
import json
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
from .huggingface_recommendation import get_recommendations
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import requests

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
    product = get_object_or_404(Product, name=product_name)
    reviews = product.reviews.all()

    sentiment_counts = reviews.aggregate(
        positive=Count(Case(When(sentiment='positive', then=1))),
        negative=Count(Case(When(sentiment='negative', then=1))),
        neutral=Count(Case(When(sentiment='neutral', then=1)))
    )

    total_reviews = sum(sentiment_counts.values())
    satisfaction_rate = ((sentiment_counts['positive'] + (sentiment_counts['neutral']/2)) / total_reviews * 100) if total_reviews > 0 else 0

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
        comment = filter_profanity(request.POST.get('comment'))
        rating = request.POST.get('rating')
        Review.objects.create(product=product, user=request.user, comment=comment, rating=rating)
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
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()

    # Calculate subtotal using Decimal to avoid float issues
    cart_subtotal = sum(Decimal(item.product.price) * item.quantity for item in cart_items)
    cart_total = cart_subtotal + Decimal('3.00')  # Adding flat rate shipping

    # Calculate total price for each item and attach to each cart item
    for item in cart_items:
        item.total_price = Decimal(item.product.price) * item.quantity

    # Fetch all products in the catalog for recommendation comparison
    all_products = Product.objects.all()

    # Get product recommendations using the Hugging Face model
    recommended_products = get_recommendations(cart_items, all_products)

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
        'recommended_products': recommended_products,  # Pass recommendations to the template
    }
    return render(request, 'cart.html', context)


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Read the JSON body
    data = json.loads(request.body)
    quantity = int(data.get('quantity', 1))  # Default to 1 if not provided

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += quantity  # Update quantity if the item already exists

    cart_item.save()

    return JsonResponse({'success': True, 'redirect_url': reverse('cart')})  # Send a JSON response with the redirect URL



@login_required
@require_POST
def update_cart_item(request, item_id):
    print(f"Updating cart item with ID: {item_id}")  # Debugging line
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        print(f"Current cart item: {cart_item}")  # Debugging line
        data = json.loads(request.body)
        new_quantity = data.get('quantity')

        print(f"New quantity: {new_quantity}")  # Debugging line

        if new_quantity and new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()

            return JsonResponse({
                'success': True,
                'unit_price': float(cart_item.product.price),
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)

    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)




@login_required
@require_POST
def remove_from_cart(request, item_id):
    # Get the cart item that the user wants to remove
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    # Remove the item from the cart
    cart_item.delete()

    # Return a JSON response indicating success
    return JsonResponse({'success': True})


@login_required
def checkout(request):
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()

    # Calculate subtotal using Decimal to avoid float issues
    cart_subtotal = sum(Decimal(item.product.price) * item.quantity for item in cart_items)
    cart_total = cart_subtotal + Decimal('3.00')  # Adding flat rate shipping

    # Pass cart items and totals to the context
    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
    }

    if request.method == 'POST':
        # Get billing details from the form (as you have already done)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        payment_method = request.POST.get('payment_method')

        # Calculate total price for the entire order
        total_order_price = 0
        cart_items_order = []
        for item in cart_items:
            total_price = Decimal(item.product.price) * item.quantity
            total_order_price += total_price
            cart_items_order.append((item.product.id, item.quantity, total_price))

        # Create the order
        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            address=address,
            city=city,
            country=country,
            zip_code=zip_code,
            mobile=mobile,
            email=email,
            payment_method=payment_method,
            total_price=total_order_price
        )

        # Create the order items
        for item in cart_items_order:
            product = get_object_or_404(Product, id=item[0])  # Fetch product or return 404
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item[1],
                total_price=item[2]
            )

        # Clear the cart by deleting all items from the cart
        cart.items.all().delete()

        return redirect('/products/shop/')

    return render(request, 'chackout.html', context)





@login_required
def contact(request):
    return render(request, 'contact.html')

@login_required
def testimonial(request):
    return render(request, 'testimonial.html')