import os
import sys
from django.test import RequestFactory

# Preparar entorno Django
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmAPI.settings')
import django
django.setup()

from rest_api.models import Film
from rest_api import views

rf = RequestFactory()

print('Películas en DB:')
for f in Film.objects.all().values('id','title','year'):
    print(f)

# Probar get para id=1
req = rf.get('/movies/1/')
resp = views.get_movie(req, film_id=1)
print('\nRespuesta para film_id=1: status', resp.status_code, 'content:', resp.data if hasattr(resp,'data') else resp.content)

# Probar get para id=2
req2 = rf.get('/movies/2/')
resp2 = views.get_movie(req2, film_id=2)
print('\nRespuesta para film_id=2: status', resp2.status_code, 'content:', resp2.data if hasattr(resp2,'data') else resp2.content)

# Probar get para id=999 (no existe)
req3 = rf.get('/movies/999/')
resp3 = views.get_movie(req3, film_id=999)
print('\nRespuesta para film_id=999: status', resp3.status_code, 'content:', resp3.data if hasattr(resp3,'data') else resp3.content)

