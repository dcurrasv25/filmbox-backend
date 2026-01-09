from django.urls import path
from .views import MarkWatchedView

urlpatterns = [
    path('watched/<int:movieId>/', MarkWatchedView.as_view(), name='mark_watched'),
]
