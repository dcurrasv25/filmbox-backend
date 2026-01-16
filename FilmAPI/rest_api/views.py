from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Film,
    Comment,
    WatchedFilm,
    FavoriteFilm,
    FilmBoxUser,
    WishlistFilm,
)
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

# --- Views ---


class MovieReviewView(APIView):

    def get(self, request, id):
        try:
            film = Film.objects.get(id=id)
        except Film.DoesNotExist:
            return Response(
                {"error": "Film not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        comments = (
            Comment.objects
            .filter(film=film)
            .select_related("user")
            .order_by("-created_at")[:3]
        )

        reviews = []
        for comment in comments:
            reviews.append({
                "author": comment.user.username,
                "rating": comment.score,
                "comment": comment.content,
                "date": comment.created_at.astimezone().strftime('%Y-%m-%d %H:%M:%S'),
            })

        return Response(
            {
                "movie_id": film.id,
                "total_reviews": Comment.objects.filter(film=film).count(),
                "preview": reviews
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, id):
        user = get_authenticated_user(request)
        if not user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

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
            return Response({
                "author": user.username,
                "rating": existing_comment.score,
                "comment": existing_comment.content,
                "date": existing_comment.updated_at.astimezone().strftime('%Y-%m-%d %H:%M:%S'),
            }, status=status.HTTP_200_OK)

        new_comment = Comment.objects.create(
            user=user, film=film, score=rating, content=comment_text
        )
        return Response({
            "author": user.username,
            "rating": new_comment.score,
            "comment": new_comment.content,
            "date": new_comment.created_at.astimezone().strftime('%Y-%m-%d %H:%M:%S'),
        }, status=status.HTTP_201_CREATED)


class GetMovieView(APIView):
    def get(self, request, film_id):
        try:
            film = Film.objects.get(pk=film_id)
        except Film.DoesNotExist:
            return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FilmSerializer(film)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkWatchedView(APIView):
    def put(self, request, movie_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({"detail": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            film = Film.objects.get(id=movie_id)
        except Film.DoesNotExist:
            return Response({"detail": "The film does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if WatchedFilm.objects.filter(user=user, film=film).exists():
            return Response({"detail": "Film was already marked as watched."}, status=status.HTTP_200_OK)

        WatchedFilm.objects.create(user=user, film=film)
        return Response({"detail": "Film marked as watched for the first time."}, status=status.HTTP_201_CREATED)


class DeleteWatchedView(APIView):
    def delete(self, request, movie_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({"detail": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            film = Film.objects.get(pk=movie_id)
            entry = WatchedFilm.objects.get(user=user, film=film)
        except (Film.DoesNotExist, WatchedFilm.DoesNotExist):
            return Response({"detail": "Movie not found in watched list."}, status=status.HTTP_404_NOT_FOUND)

        entry.delete()
        return Response({"detail": "Movie removed from watched list."}, status=status.HTTP_200_OK)


class DeleteLikeView(APIView):
    def delete(self, request, movie_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({"detail": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            like = FavoriteFilm.objects.get(user=user, film_id=movie_id)
        except FavoriteFilm.DoesNotExist:
            return Response({"detail": "Like not found"}, status=status.HTTP_404_NOT_FOUND)

        like.delete()
        return Response({"detail": "Like deleted"}, status=status.HTTP_204_NO_CONTENT)


class DeleteWishlistView(APIView):
    def delete(self, request, movie_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({"detail": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            film = Film.objects.get(pk=movie_id)
        except Film.DoesNotExist:
            return Response({"detail": "Movie not found."}, status=status.HTTP_404_NOT_FOUND)

        user_qs = WishlistFilm.objects.filter(user=user, film=film)
        if user_qs.exists():
            user_qs.delete()
            return Response({"detail": "Movie removed from wishlist."}, status=status.HTTP_200_OK)

        return Response({"detail": "Movie not in wishlist."}, status=status.HTTP_404_NOT_FOUND)


class WishlistFilmView(APIView):
    def put(self, request, film_id):
        user = get_authenticated_user(request)
        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            film = Film.objects.get(id=film_id)
        except Film.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if WishlistFilm.objects.filter(user=user, film=film).exists():
            return Response(status=status.HTTP_200_OK)

        WishlistFilm.objects.create(user=user, film=film)
        return Response(status=status.HTTP_201_CREATED)


class SearchMoviesView(APIView):
    def get(self, request):
        query = request.query_params.get('query')
        if not query or not query.strip():
            return Response({"error": "Invalid query parameter"}, status=status.HTTP_400_BAD_REQUEST)

        films = Film.objects.filter(title__icontains=query).order_by('id')
        serializer = FilmSerializer(films, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

