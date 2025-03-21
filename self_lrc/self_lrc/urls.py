"""
URL configuration for self_lrc project.

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
from django.contrib import admin
from django.urls import path

from app import views as views_app
from api import views as views_api
urlpatterns = [
    path('admin/', admin.site.urls),
    path('<str:username>/api/search', views_api.search_songs,name='search'),
    path('<str:username>/api/get', views_api.get_songs,name='search'),
    path('', views_app.get_home,name='home'),
]
