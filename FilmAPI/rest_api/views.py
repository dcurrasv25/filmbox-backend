import secrets

from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .authentication import FilmBoxAuthentication

from .models import (
    Film,
    Comment,
    WatchedFilm,
    FavoriteFilm,
    FilmBoxUser,
    WishlistFilm,
)
from .serializers import FilmSerializer, UserSerializer


from django.contrib.auth.hashers import check_password # Importante para verificar el hash

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password') # Esta es la contraseña en texto plano que viene de Android

        try:
            # 1. Buscamos al usuario SOLO por el nombre
            user = FilmBoxUser.objects.get(username=username)

            # 2. Comparamos la contraseña recibida con el hash de la base de datos
            if check_password(password, user.encrypted_password):
                # Si coincide, generamos el token
                token = secrets.token_hex(25)
                user.session_token = token
                user.save()

                return Response({
                    "token": token,
                    "username": user.username,
                    "detail": "Login exitoso"
                }, status=status.HTTP_200_OK)
            else:
                # Si la contraseña no coincide con el hash
                return Response(
                    {"detail": "Credenciales inválidas"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except FilmBoxUser.DoesNotExist:
            # Si el usuario ni siquiera existe
            return Response(
                {"detail": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )

# --- Views ---
class MovieReviewView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, id):
        try:
            film = Film.objects.get(id=id)
        except Film.DoesNotExist:
            return Response(
                {"error": "Film not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        show_all = request.query_params.get('all', 'false').lower() == 'true'
        comments_qs = Comment.objects.filter(film=film).select_related("user").order_by("-created_at")

        if not show_all:
            comments_qs = comments_qs[:3]

        reviews = []
        for comment in comments_qs:
            reviews.append({
                "author": comment.user.username,
                "rating": comment.score,
                "comment": comment.content,
                "date": comment.created_at.astimezone().strftime('%Y-%m-%d %H:%M:%S'),
            })

        if show_all:
            return Response(reviews, status=status.HTTP_200_OK)

        return Response(
            {
                "movie_id": film.id,
                "total_reviews": Comment.objects.filter(film=film).count(),
                "preview": reviews
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, id):
        user = request.user

        try:
            film = Film.objects.get(id=id)
        except Film.DoesNotExist:
            return Response({"error": "Film not found"}, status=status.HTTP_404_NOT_FOUND)

        rating = request.data.get("rating")
        comment_text = request.data.get("comment")

        if rating is None:
            return Response({"error": "rating is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = float(rating)
        except (TypeError, ValueError):
            return Response({"error": "rating must be a number"}, status=status.HTTP_400_BAD_REQUEST)

        if rating < 1 or rating > 5 or (rating * 2 != int(rating * 2)):
            return Response({"error": "rating must be between 1 and 5 (integers or .5)"}, status=status.HTTP_400_BAD_REQUEST)

        if comment_text is None or not str(comment_text).strip():
            return Response({"error": "comment is required"}, status=status.HTTP_400_BAD_REQUEST)

        existing_comment = Comment.objects.filter(user=user, film=film).first()

        if existing_comment:
            existing_comment.score = rating
            existing_comment.content = comment_text
            existing_comment.save()

            return Response(
                {
                    "author": user.username,
                    "rating": existing_comment.score,
                    "comment": existing_comment.content,
                    "date": existing_comment.updated_at.astimezone().strftime('%Y-%m-%d %H:%M:%S'),
                },
                status=status.HTTP_200_OK)

        new_comment = Comment.objects.create(
            user=user,
            film=film,
            score=rating,
            content=comment_text
        )
        return Response(
            {
                "author": user.username,
                "rating": new_comment.score,
                "comment": new_comment.content,
                "date": new_comment.created_at.astimezone().strftime('%Y-%m-%d %H:%M:%S'),
            },
            status=status.HTTP_201_CREATED
        )


class GetMovieView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(pk=movie_id)
        except Film.DoesNotExist:
            return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FilmSerializer(film)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WatchedView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(id=movie_id)
        except Film.DoesNotExist:
            return Response({"detail": "The film does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if WatchedFilm.objects.filter(user=user, film=film).exists():
            return Response({"detail": "Film was already marked as watched."}, status=status.HTTP_200_OK)

        WatchedFilm.objects.create(user=user, film=film)
        return Response({"detail": "Film marked as watched for the first time."}, status=status.HTTP_201_CREATED)


    def delete(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(pk=movie_id)
            entry = WatchedFilm.objects.get(user=user, film=film)
        except (Film.DoesNotExist, WatchedFilm.DoesNotExist):
            return Response({"detail": "Movie not found in watched list."}, status=status.HTTP_404_NOT_FOUND)

        entry.delete()
        return Response({"detail": "Movie removed from watched list."}, status=status.HTTP_200_OK)



class FavoriteFilmView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(id=movie_id)
        except Film.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if FavoriteFilm.objects.filter(user=user, film=film).exists():
            return Response(status=status.HTTP_200_OK)

        FavoriteFilm.objects.create(user=user, film=film)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, movie_id):
        user = request.user

        try:
            like = FavoriteFilm.objects.get(user=user, film_id=movie_id)
        except FavoriteFilm.DoesNotExist:
            return Response({"detail": "Like not found"}, status=status.HTTP_404_NOT_FOUND)

        like.delete()
        return Response({"detail": "Like deleted"}, status=status.HTTP_204_NO_CONTENT)


class WishlistFilmView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(id=movie_id)
        except Film.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if WishlistFilm.objects.filter(user=user, film=film).exists():
            return Response(status=status.HTTP_200_OK)

        WishlistFilm.objects.create(user=user, film=film)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(pk=movie_id)
        except Film.DoesNotExist:
            return Response({"detail": "Movie not found."}, status=status.HTTP_404_NOT_FOUND)

        user_qs = WishlistFilm.objects.filter(user=user, film=film)
        if user_qs.exists():
            user_qs.delete()
            return Response({"detail": "Movie removed from wishlist."}, status=status.HTTP_200_OK)

        return Response({"detail": "Movie not in wishlist."}, status=status.HTTP_404_NOT_FOUND)


class SearchMoviesView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request):
        user = request.user

        query = request.query_params.get('query')
        if not query or not query.strip():
            return Response({"error": "Invalid query parameter"}, status=status.HTTP_400_BAD_REQUEST)

        films = Film.objects.filter(title__icontains=query).order_by('id')
        serializer = FilmSerializer(films, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SearchUsersView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user

        query = request.query_params.get('query')

        if not query or not query.strip():
            return Response(
                {"error": "Invalid query parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            users = FilmBoxUser.objects.filter(username__icontains=query).order_by('id')
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )