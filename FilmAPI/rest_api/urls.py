from django.urls import path
from .views import GetMovieView
from .views import MarkWatchedView
from .views import DeleteWatchedView

urlpatterns = [
    path('movies/<int:film_id>', GetMovieView.as_view(), name='get_movie'),
    path('watched/<int:movie_id>', MarkWatchedView.as_view(), name='mark_watched'),
    path('watched/<int:movie_id>', DeleteWatchedView.as_view(), name='delete_watched_movie'),
]