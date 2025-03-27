from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='category_list'),  
    path('list/', views.product_list, name='product_list'),  
    path('add/', views.add_product, name='add_product'), 
]
