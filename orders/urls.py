from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order-list'),
    path('create/', views.create_order, name='create-order'),
    path('<int:order_id>/', views.order_detail, name='order-detail'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel-order'),
] 