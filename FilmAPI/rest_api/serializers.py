from rest_framework import serializers
from .models import Film, Category, Comment

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    nombre = serializers.CharField(source='title')

    class Meta:
        model = Category
        fields = ('id', 'nombre')

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

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('film', 'content', 'score')

