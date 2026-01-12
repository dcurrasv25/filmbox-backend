from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Film, Category
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import FilmSerializer

# Create your views here.

@api_view(['GET'])
def get_movie(request, film_id):
    """Devuelve los datos detallados de una película en formato JSON usando DRF.

    Responses:
    - 200: datos de la película
    - 404: {"error": "Movie not found"}
    """
    try:
        film = Film.objects.get(pk=film_id)
    except Film.DoesNotExist:
        return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = FilmSerializer(film)
    return Response(serializer.data, status=status.HTTP_200_OK)
