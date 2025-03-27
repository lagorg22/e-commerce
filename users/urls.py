from django.urls import path
from .views import register_user, login_user, user_profile, logout_user, register_admin

urlpatterns = [
    path('register/', register_user, name='register'),
    path('register/admin/', register_admin, name='register-admin'),
    path('login/', login_user, name='login'),
    path('profile/', user_profile, name='profile'),
    path('logout/', logout_user, name='logout'),
]
