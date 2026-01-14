import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmAPI.settings')
import django
django.setup()
from rest_api.models import Film

films = Film.objects.all().values('pk','title','year')
for f in films:
    print(f)
if not films:
    print('No films found')

