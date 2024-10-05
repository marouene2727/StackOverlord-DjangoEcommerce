from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('notFound/', views.notFound, name='notFound'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
    path('shopDetails/', views.shopDetails, name='shopDetails'),
    path('testimonial/', views.testimonial, name='testimonial'),
    # Déconnexion avec redirection vers la page 'home'
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

]
