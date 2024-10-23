from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [

    # Shop and product details
    path('shop/', views.shop, name='shop'),
    path('shopDetails/<str:product_name>/', views.shopDetails, name='shopDetails'),

    # Reviews
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    path('products/update-review/<int:review_id>/', views.update_review, name='update_review'),
    path('products/delete-review/<int:review_id>/', views.delete_review, name='delete_review'),

    # Cart functionality
    path('products/cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),


]
