from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import FavoriteFilm, FilmBoxUser


def get_user_from_token(request):
    auth = request.headers.get('Authorization')

    if not auth or not auth.startswith('Bearer '):
        return None

    token = auth.split(' ')[1]

    try:
        return FilmBoxUser.objects.get(session_token=token)
    except FilmBoxUser.DoesNotExist:
        return None


class DeleteLikeView(APIView):

    def delete(self, request, movie_id):
        user = get_user_from_token(request)
        if not user:
            return Response(
                {"detail": "User not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            like = FavoriteFilm.objects.get(user=user, film_id=movie_id)
        except FavoriteFilm.DoesNotExist:
            return Response(
                {"detail": "Like not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        like.delete()
        return Response(
            {"detail": "Like deleted"},
            status=status.HTTP_204_NO_CONTENT
        )



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Film, WatchedFilm, FilmBoxUser
from .serializers import FilmSerializer


def get_authenticated_user(request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth[len("Bearer "):].strip()
    try:
        return FilmBoxUser.objects.get(session_token=token)
    except FilmBoxUser.DoesNotExist:
        return None

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

class   MarkWatchedView(APIView):

    def put(self, request, movie_id):
        user = get_authenticated_user(request)
        if not user:
            return Response(
                {"detail": "User not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            film = Film.objects.get(id=movie_id)
        except Film.DoesNotExist:
            return Response(
                {"detail": "The film does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        if WatchedFilm.objects.filter(user=user, film=film).exists():
            return Response(
                {"detail": "Film was already marked as watched."},
                status=status.HTTP_200_OK
            )

        WatchedFilm.objects.create(user=user, film=film)
        return Response(
            {"detail": "Film marked as watched for the first time."},
            status=status.HTTP_201_CREATED
        )


class DeleteWatchedView(APIView):

    def delete(self, request, movie_id):
        # 401 – Usuario no autenticado
        user = get_authenticated_user(request)
        if user is None:
            return Response(
                {"detail": "User not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 404 – La película no existe
        try:
            film = Film.objects.get(pk=movie_id)
        except Film.DoesNotExist:
            return Response(
                {"detail": "Movie not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 404 – La película no estaba en watched de este usuario
        try:
            entry = WatchedFilm.objects.get(user=user, film=film)
        except WatchedFilm.DoesNotExist:
            return Response(
                {"detail": "Movie not in watched list."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 200 – Se elimina
        entry.delete()
        return Response(
            {"detail": "Movie removed from watched list."},
            status=status.HTTP_200_OK
        )