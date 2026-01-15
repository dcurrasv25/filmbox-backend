from datetime import timezone

from django.db import models

class FilmBoxUser(models.Model):
  username = models.CharField(unique=True, max_length=100)
  encrypted_password = models.CharField(max_length=100)
  # Without profile picture - let's just add a default image in the Android app
  session_token = models.CharField(unique=True, max_length=100)

class Category(models.Model):
  title = models.CharField(max_length=100, unique=True)
  image_url = models.CharField(max_length=200) # e.g.: http://static.com/front.jpg

class Film(models.Model):
  title = models.CharField(max_length=100)
  description = models.CharField(max_length=100)
  image_url = models.CharField(max_length=200) # e.g.: http://static.com/front.jpg
  film_url = models.CharField(max_length=200)
  trailer_url = models.CharField(max_length=200) # e.g. https://youtube.com/watch?...
  year = models.IntegerField()
  length = models.IntegerField() # e.g.: 127
  director = models.CharField(max_length=100)

class CategoryFilm(models.Model):
  category = models.ForeignKey(Category, on_delete=models.CASCADE)
  film = models.ForeignKey(Film, on_delete=models.CASCADE)

class FavoriteFilm(models.Model):
  user = models.ForeignKey(FilmBoxUser, on_delete=models.CASCADE)
  film = models.ForeignKey(Film, on_delete=models.CASCADE)

class WishlistFilm(models.Model):
  user = models.ForeignKey(FilmBoxUser, on_delete=models.CASCADE)
  film = models.ForeignKey(Film, on_delete=models.CASCADE)

class WatchedFilm(models.Model):
  user = models.ForeignKey(FilmBoxUser, on_delete=models.CASCADE)
  film = models.ForeignKey(Film, on_delete=models.CASCADE)

class Comment(models.Model):
  user = models.ForeignKey(FilmBoxUser, on_delete=models.CASCADE)
  film = models.ForeignKey(Film, on_delete=models.CASCADE)
  content = models.CharField(max_length=200)
  score = models.IntegerField() # 1-5

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
      return f"{self.user} - {self.film} ({self.score})"
