from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [

    path('shop/', views.shop, name='shop'),
    path('shopDetails/<str:product_name>/', views.shopDetails, name='shopDetails'),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),







]