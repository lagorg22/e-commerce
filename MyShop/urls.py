"""
URL configuration for MyShop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root showing all available endpoints.
    """
    return Response({
        'users': {
            'register': reverse('register', request=request, format=format),
            'register_admin': reverse('register-admin', request=request, format=format),
            'login': reverse('login', request=request, format=format),
            'profile': reverse('profile', request=request, format=format),
            'logout': reverse('logout', request=request, format=format),
            'change_password': reverse('change-password', request=request, format=format),
            'delete_account': reverse('delete-account', request=request, format=format),
            'deposit': reverse('deposit-funds', request=request, format=format),
            'transactions': reverse('transaction-history', request=request, format=format),
        },
        'products': {
            'categories': reverse('category_list', request=request, format=format),
            'list': reverse('product_list', request=request, format=format),
            'add': reverse('add_product', request=request, format=format),
        },
        'cart': {
            'view': reverse('view-cart', request=request, format=format),
            'add': reverse('add-to-cart', request=request, format=format),
        },
        'orders': {
            'list': reverse('order-list', request=request, format=format),
            'create': reverse('create-order', request=request, format=format),
        },
        'docs': reverse('schema-swagger', request=request, format=format),
    })

schema_view = get_schema_view(
    openapi.Info(
        title='E-COMMERCE STORE API',
        default_version='v1',
        description='This is the API for E-COMMERCE application',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='gorgolasha@gmail.com')
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=(SessionAuthentication, TokenAuthentication),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api-root'),
    path('products/', include('products.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger'),
    path('users/', include('users.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
