from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as authViews
from .views import CustomPasswordResetView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('passwordreset/done/', authViews.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', authViews.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('passwordreset/', CustomPasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('reset/password/complete/', authViews.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('home/', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('notFound/', views.notFound, name='notFound'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
    path('shopDetails/', views.shopDetails, name='shopDetails'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.user_profile, name='user_profile'),  # Pour afficher le profil
    path('profile/update/', views.update_user_profile, name='update_user_profile'),
    path('send-email/', views.send_test_email, name='send_test_email'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
