from django.urls import path
from . import views

urlpatterns = [
    path('watched/<int:movie_id>/', views.delete_watched_movie, name='delete_watched_movie'),
]