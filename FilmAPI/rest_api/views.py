from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Film
from .serializers import FilmSerializer


class SearchMoviesView(APIView):

    def get(self, request):
        # Leer ?query=
        query = request.query_params.get('query')

        # 400 Bad Request si falta o está vacío
        if query is None or not query.strip():
            return Response(
                {"error": "Invalid query parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Búsqueda por título (case-insensitive)
        films = Film.objects.filter(title__icontains=query).order_by('id')

        # Serializar lista
        serializer = FilmSerializer(films, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)