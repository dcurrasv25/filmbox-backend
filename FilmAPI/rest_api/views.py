from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Film, Category

# Create your views here.

@require_http_methods(["GET"])
def get_movie(request, film_id):
    """Devuelve los datos detallados de una película en formato JSON.

    Responses:
    - 200: datos de la película
    - 404: {"error": "Movie not found"}
    - 405: método no permitido (manejada por el decorador)
    """
    try:
        film = Film.objects.get(pk=film_id)
    except Film.DoesNotExist:
        return JsonResponse({"error": "Movie not found"}, status=404)

    # Obtener categorías relacionadas
    categorias_qs = Category.objects.filter(categoryfilm__film=film).distinct()
    categorias = [{"id": c.pk, "nombre": c.title} for c in categorias_qs]

    director_obj = {"id": None, "nombre": film.director or ""}

    data = {
        "id": film.pk,
        "title": film.title,
        "year": film.year,
        "duration": film.length,
        "director": director_obj,
        "description": film.description,
        "categorias": categorias,
        "image_url": film.image_url,
        "film_url": getattr(film, 'film_url', ''),
        "trailer_url": getattr(film, 'trailer_url', ''),
    }

    return JsonResponse(data, status=200)
