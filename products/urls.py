from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [

    path('shop/', views.shop, name='shop'),
    path('shopDetails/<str:product_name>/', views.shopDetails, name='shopDetails'),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    #path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    
    path('products/update-review/<int:review_id>/', views.update_review, name='update_review'),

path('products/delete-review/<int:review_id>/', views.delete_review, name='delete_review'),


    








]