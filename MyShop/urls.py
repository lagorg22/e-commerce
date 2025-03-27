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

schema_view = get_schema_view(
    openapi.Info(
        title='Event Manager API',
        default_version='v1',
        description='This is the API for event manager application',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='irakli.tabatadze.80@gmail.com')
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
