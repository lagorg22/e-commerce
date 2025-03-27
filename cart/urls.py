from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_to_cart, name='add-to-cart'),
    path('view/', views.view_cart, name='view-cart'),
    path('remove/<int:cart_item_id>/', views.remove_from_cart, name='remove-from-cart'),
]
