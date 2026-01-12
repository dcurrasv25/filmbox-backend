from django.urls import path
from .views import MarkWatchedView

urlpatterns = [
    path('watched/<int:movie_id>', MarkWatchedView.as_view(), name='mark_watched'),
]