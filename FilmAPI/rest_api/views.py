from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Film
from .serializers import FilmSerializer


class GetMovieView(APIView):

    def get(self, request, film_id):
        try:
            film = Film.objects.get(pk=film_id)
        except Film.DoesNotExist:
            return Response(
                {"error": "Movie not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FilmSerializer(film)
        return Response(serializer.data, status=status.HTTP_200_OK)
