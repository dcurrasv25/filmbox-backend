from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import FilmBoxUser, Film, WatchedFilm


def get_authenticated_user(request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth[len("Bearer "):].strip()
    try:
        return FilmBoxUser.objects.get(session_token=token)
    except FilmBoxUser.DoesNotExist:
        return None


@require_http_methods(["DELETE"])
def delete_watched_movie(request, movie_id):
    # 401 – Usuario no autenticado
    user = get_authenticated_user(request)
    if user is None:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # 404 – La película no existe
    try:
        film = Film.objects.get(pk=movie_id)
    except Film.DoesNotExist:
        return JsonResponse({"error": "Movie not found"}, status=404)

    # 404 – La película no estaba en watched de este usuario
    try:
        entry = WatchedFilm.objects.get(user=user, film=film)
    except WatchedFilm.DoesNotExist:
        return JsonResponse({"error": "Movie not in watched list"}, status=404)

    # 200 – Se elimina
    entry.delete()
    return JsonResponse({}, status=200)
