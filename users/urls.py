from django.urls import path
from .views import register_user, login_user, user_profile, logout_user, register_admin, change_password, delete_account

urlpatterns = [
    path('register/', register_user, name='register'),
    path('register/admin/', register_admin, name='register-admin'),
    path('login/', login_user, name='login'),
    path('profile/', user_profile, name='profile'),
    path('logout/', logout_user, name='logout'),
    path('change-password/', change_password, name='change-password'),
    path('delete-account/', delete_account, name='delete-account'),
]
