from django.urls import path
from .views import (
    MovieReviewView,
    FavoriteFilmView,
    GetMovieView,
    WatchedView,
    WishlistFilmView,
    SearchMoviesView,
    SearchUsersView,
    UserRegistrationView,
)

urlpatterns = [
    path('movies/<int:movie_id>', GetMovieView.as_view(), name='get_movie'),
    path('watched/<int:movie_id>', WatchedView.as_view(), name='watched'),
    path('movies/<int:id>/reviews', MovieReviewView.as_view(), name='movie_review'),
    path('movies', SearchMoviesView.as_view(), name='search_movies'),
    path('favorites/<int:movie_id>', FavoriteFilmView.as_view(), name='favorite_film'),
    path('wishlist/<int:movie_id>', WishlistFilmView.as_view(), name='wishlist'),
    path('users', SearchUsersView.as_view(), name='search_users'),
    path('register', UserRegistrationView.as_view(), name='register'),
]
