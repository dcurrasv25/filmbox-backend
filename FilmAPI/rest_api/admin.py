from django.contrib import admin

# Register your models here.
from .models import Category, FilmBoxUser , Film, CategoryFilm, FavoriteFilm, WishlistFilm, WatchedFilm, Comment
admin.site.register(Category)
admin.site.register(FilmBoxUser)
admin.site.register(Film)
admin.site.register(CategoryFilm)
admin.site.register(FavoriteFilm)
admin.site.register(WishlistFilm)
admin.site.register(WatchedFilm)
admin.site.register(Comment)

