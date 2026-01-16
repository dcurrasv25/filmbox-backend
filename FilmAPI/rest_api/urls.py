from django.urls import path
from .views import MovieReviewView
from .views import DeleteLikeView
from .views import GetMovieView
from .views import MarkWatchedView
from .views import DeleteWatchedView
from .views import DeleteWishlistView
from .views import SearchMoviesView
from .views import WatchlistFilmView

urlpatterns = [
    path('movies/<int:film_id>', GetMovieView.as_view(), name='get_movie'),
    path('watched/<int:movie_id>', MarkWatchedView.as_view(), name='mark_watched'),
    path('watched/<int:movie_id>', DeleteWatchedView.as_view(), name='delete_watched_movie'),
    path('favorites/<int:movie_id>', DeleteLikeView.as_view(), name='delete_like'),
    path('movies/<int:id>/reviews', MovieReviewView.as_view(), name='movie_review'),
    path('wishlist/<int:movie_id>', DeleteWishlistView.as_view(), name='delete_wishlist'),
    path('movies', SearchMoviesView.as_view(), name='search_movies'),
    path('wishlist/<int:film_id>', WishlistFilmView.as_view(), name='wishlist'),
]