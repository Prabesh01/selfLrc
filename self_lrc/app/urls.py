from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/search/', views.search_songs,name='search')
]
