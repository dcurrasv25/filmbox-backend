import secrets

from django.contrib.auth.hashers import check_password
from django.utils.timezone import now

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import FilmBoxAuthentication
from .models import (
    Film,
    Category,
    Comment,
    WatchedFilm,
    FavoriteFilm,
    FilmBoxUser,
    WishlistFilm,
)
from .serializers import (
    FilmSerializer,
    FilmLiteSerializer,
    CategorySerializer,
    UserSerializer,
    UserRegistrationSerializer,
)


# =========================
# AUTH
# =========================

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            user = FilmBoxUser.objects.get(username=username)

            if check_password(password, user.encrypted_password):
                token = secrets.token_hex(25)
                user.session_token = token
                user.save()

                return Response(
                    {
                        "token": token,
                        "username": user.username,
                        "detail": "Login exitoso",
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"detail": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except FilmBoxUser.DoesNotExist:
            return Response(
                {"detail": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        token = request.data.get("token")

        if not token or not str(token).strip():
            return Response(
                {"detail": "Token inválido o expirado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = FilmBoxUser.objects.get(session_token=token)
        except FilmBoxUser.DoesNotExist:
            return Response(
                {"detail": "Token inválido o expirado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.session_token = None
        user.save(update_fields=["session_token"])

        return Response(
            {"detail": "Logout exitoso"},
            status=status.HTTP_200_OK,
        )


# =========================
# CATEGORIES
# =========================

class CategoryListView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        categories = Category.objects.all().order_by('title')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryMoviesView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, category_id):
        if not Category.objects.filter(pk=category_id).exists():
            return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        films = (
            Film.objects
            .filter(categoryfilm__category_id=category_id)
            .only("id", "title", "year", "image_url", "length")
            .order_by("id")
            .distinct()
        )

        serializer = FilmLiteSerializer(films, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# =========================
# REVIEWS
# =========================

class MovieReviewView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, id):
        try:
            film = Film.objects.get(id=id)
        except Film.DoesNotExist:
            return Response(
                {"error": "Film not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        show_all = request.query_params.get("all", "false").lower() == "true"

        comments = (
            Comment.objects
            .filter(film=film)
            .select_related("user")
            .order_by("-created_at")
        )

        if not show_all:
            comments = comments[:3]

        reviews = [
            {
                "author": comment.user.username,
                "rating": comment.score,
                "comment": comment.content,
                "date": comment.created_at.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
            }
            for comment in comments
        ]

        if show_all:
            return Response(reviews, status=status.HTTP_200_OK)

        return Response(
            {
                "movie_id": film.id,
                "total_reviews": Comment.objects.filter(film=film).count(),
                "preview": reviews,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, id):
        user = request.user

        try:
            film = Film.objects.get(id=id)
        except Film.DoesNotExist:
            return Response(
                {"error": "Film not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        rating = request.data.get("rating")
        comment_text = request.data.get("comment")

        if rating is None:
            return Response(
                {"error": "rating is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            rating = float(rating)
        except (TypeError, ValueError):
            return Response(
                {"error": "rating must be a number"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if rating < 1 or rating > 5 or rating * 2 != int(rating * 2):
            return Response(
                {"error": "rating must be between 1 and 5 (integers or .5)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not comment_text or not str(comment_text).strip():
            return Response(
                {"error": "comment is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment, created = Comment.objects.update_or_create(
            user=user,
            film=film,
            defaults={
                "score": rating,
                "content": comment_text,
            },
        )

        return Response(
            {
                "author": user.username,
                "rating": comment.score,
                "comment": comment.content,
                "date": (
                    comment.updated_at if not created else comment.created_at
                ).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


# =========================
# MOVIES
# =========================

class GetMovieView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, movie_id):
        try:
            film = Film.objects.get(pk=movie_id)
        except Film.DoesNotExist:
            return Response(
                {"error": "Movie not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FilmSerializer(film)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =========================
# WATCHED
# =========================

class WatchedListView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        watched = WatchedFilm.objects.filter(user=user).select_related("film")
        films = [w.film for w in watched]
        serializer = FilmSerializer(films, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WatchedDetailView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(id=movie_id)
        except Film.DoesNotExist:
            return Response(
                {"detail": "The film does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if WatchedFilm.objects.filter(user=user, film=film).exists():
            return Response(
                {"detail": "Film was already marked as watched."},
                status=status.HTTP_200_OK,
            )

        WatchedFilm.objects.create(user=user, film=film)
        return Response(
            {"detail": "Film marked as watched for the first time."},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(pk=movie_id)
            entry = WatchedFilm.objects.get(user=user, film=film)
        except (Film.DoesNotExist, WatchedFilm.DoesNotExist):
            return Response(
                {"detail": "Movie not found in watched list."},
                status=status.HTTP_404_NOT_FOUND,
            )

        entry.delete()
        return Response(
            {"detail": "Movie removed from watched list."},
            status=status.HTTP_200_OK,
        )



# =========================
# FAVORITES
# =========================

class FavoriteFilmView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(id=movie_id)
        except Film.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        FavoriteFilm.objects.get_or_create(user=user, film=film)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, movie_id):
        user = request.user

        deleted, _ = FavoriteFilm.objects.filter(
            user=user,
            film_id=movie_id,
        ).delete()

        if not deleted:
            return Response(
                {"detail": "Like not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"detail": "Like deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )

class FavoriteListView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        favorites = FavoriteFilm.objects.filter(user=user).select_related('film')
        films = [f.film for f in favorites]
        serializer = FilmSerializer(films, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =========================
# WISHLIST
# =========================

class WishlistView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        wishlist = WishlistFilm.objects.filter(user=user).select_related('film')
        films = [w.film for w in wishlist]
        serializer = FilmSerializer(films, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class WishlistFilmView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, movie_id):
        user = request.user

        try:
            film = Film.objects.get(id=movie_id)
        except Film.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        WishlistFilm.objects.get_or_create(user=user, film=film)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, movie_id):
        user = request.user

        deleted, _ = WishlistFilm.objects.filter(
            user=user,
            film_id=movie_id,
        ).delete()

        if not deleted:
            return Response(
                {"detail": "Movie not in wishlist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"detail": "Movie removed from wishlist."},
            status=status.HTTP_200_OK,
        )


# =========================
# SEARCH
# =========================

class SearchMoviesView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        query = request.query_params.get("query", "").strip()
        if not query:
            return Response([], status=status.HTTP_200_OK)

        films = (
            Film.objects
            .filter(title__icontains=query)
            .only("id", "title", "year", "image_url", "length")
            [:20]
        )

        serializer = FilmLiteSerializer(films, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchUsersView(APIView):
    authentication_classes = [FilmBoxAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("query")

        if not query or not query.strip():
            return Response(
                {"error": "Invalid query parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        users = FilmBoxUser.objects.filter(username__icontains=query).order_by("id")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =========================
# REGISTRATION
# =========================

class UserRegistrationView(generics.CreateAPIView):
    queryset = FilmBoxUser.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "username": serializer.data.get("username"),
                "detail": "User created successfully",
            },
            status=status.HTTP_201_CREATED,
        )
