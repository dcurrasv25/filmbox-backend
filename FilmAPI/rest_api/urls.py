from django.urls import path
from . import views

urlpatterns = [
    path('movies/<int:film_id>/', views.get_movie, name='get_movie'),
]
