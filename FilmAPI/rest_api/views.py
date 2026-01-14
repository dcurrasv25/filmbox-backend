from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Film, Comment, FilmBoxUser
from django.utils.timezone import now

def get_authenticated_user(request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth[len("Bearer "):].strip()
    try:
        return FilmBoxUser.objects.get(session_token=token)
    except FilmBoxUser.DoesNotExist:
        return None

class MovieReviewView(APIView):
    def put(self, request, id):
        # 401 – Unauthorized
        user = get_authenticated_user(request)
        if not user:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        # 404 - Movie not found
        try:
            film = Film.objects.get(id=id)
        except Film.DoesNotExist:
            return Response(
                {"error": "Film not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        rating = request.data.get('rating')
        comment_text = request.data.get('comment')

        # 400 – Bad request (validation)
        if rating is None:
            return Response(
                {"error": "rating is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rating = float(rating)
        except (TypeError, ValueError):
            return Response(
                {"error": "rating must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if rating < 1 or rating > 5:
            return Response(
                {"error": "rating must be between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Rating must be integer or .5
        if rating * 2 != int(rating * 2):
            return Response(
                {"error": "rating must be integer or .5"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if comment_text is None or not str(comment_text).strip():
            return Response(
                {"error": "comment is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Search if exists
        existing_comment = Comment.objects.filter(user=user, film=film).first()

        if existing_comment:
            # 200 - Update review
            existing_comment.score = rating
            existing_comment.content = comment_text
            existing_comment.save()

            return Response(
                {
                    "author": user.username,
                    "rating": existing_comment.score,
                    "comment": existing_comment.content,
                    "date": now()
                },
                status=status.HTTP_200_OK
            )
        # 201 - Create review
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
                "date": now()
            },
            status=status.HTTP_201_CREATED
        )