from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Film, Category, FilmBoxUser
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title", "image_url")


class FilmSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    duration = serializers.IntegerField(source='length')
    categorias = serializers.SerializerMethodField()

    class Meta:
        model = Film
        fields = (
            'id', 'title', 'year', 'duration', 'director', 'description',
            'categorias', 'image_url', 'film_url', 'trailer_url'
        )

    def get_categorias(self, obj):
        qs = Category.objects.filter(categoryfilm__film=obj).distinct()
        return CategorySerializer(qs, many=True).data


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = FilmBoxUser
        fields = ('id', 'username', 'avatar_url')

    def get_avatar_url(self, obj):
        return "https://.../default.png"


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = FilmBoxUser
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        return FilmBoxUser.objects.create(
            username=validated_data['username'],
            encrypted_password=make_password(validated_data['password']),
            session_token=None
        )
