from django.urls import path
from .views import GetMovieView

urlpatterns = [
    path('movies/<int:film_id>', GetMovieView.as_view(), name='get_movie'),
]
