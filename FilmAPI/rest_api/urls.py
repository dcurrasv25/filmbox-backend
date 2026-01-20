from django.urls import path

from .views import (
    LoginView,
    MovieReviewView,
    FavoriteFilmView,
    GetMovieView,
    WatchedView,
    WishlistFilmView,
    WishlistView,
    SearchMoviesView,
    SearchUsersView,
    UserRegistrationView,
    LogoutView,
    FavoriteListView,
)

urlpatterns = [
    path("users/login", LoginView.as_view(), name="login"),
    path("register", UserRegistrationView.as_view(), name="register"),
    path('users/logout', LogoutView.as_view(), name='logout'),

    path("movies", SearchMoviesView.as_view(), name="search_movies"),
    path("movies/<int:movie_id>", GetMovieView.as_view(), name="get_movie"),
    path("movies/<int:id>/reviews", MovieReviewView.as_view(), name="movie_review"),

    path("watched/<int:movie_id>", WatchedView.as_view(), name="watched"),
    path("favorites", FavoriteListView.as_view(), name="favorite_list"),
    path("favorites/<int:movie_id>", FavoriteFilmView.as_view(), name="favorite_film"),
    path("wishlist", WishlistView.as_view(), name="wishlist_list"),
    path("wishlist/<int:movie_id>", WishlistFilmView.as_view(), name="wishlist"),

    path("users", SearchUsersView.as_view(), name="search_users"),
]