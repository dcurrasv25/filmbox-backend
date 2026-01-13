from django.urls import path
from .views import SearchMoviesView

urlpatterns = [
    path('movies', SearchMoviesView.as_view(), name='search_movies'),
]