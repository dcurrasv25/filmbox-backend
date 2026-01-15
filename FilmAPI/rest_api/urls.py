from django.urls import path
from .views import WatchlistFilmView

urlpatterns = [
    path('watchlist/<int:film_id>',
         WatchlistFilmView.as_view(), name='watchlist'),
]