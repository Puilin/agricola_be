"""agricola URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
<<<<<<< HEAD
from drf_yasg       import openapi
=======
from drf_yasg import openapi
>>>>>>> yh.hong

schema_view = get_schema_view(
    openapi.Info(
        title="Team 4",
        default_version='Python 3.11',
        description="Agricola API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        # contact=openapi.Contact(email="이메일"), # 부가정보
        # license=openapi.License(name="mit"),     # 부가정보
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
<<<<<<< HEAD
    path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
    path('admin/', admin.site.urls),

=======
    path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(
        cache_timeout=0), name='schema-json'),
    path(r'swagger', schema_view.with_ui(
        'swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc', schema_view.with_ui(
        'redoc', cache_timeout=0), name='schema-redoc-v1'),
    path('admin/', admin.site.urls),
>>>>>>> yh.hong
    path('', include('gameplay.urls')),
]
