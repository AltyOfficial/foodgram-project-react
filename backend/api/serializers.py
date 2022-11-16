import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from users.serializers import UserSerializer

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient Serailizer."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Tag Serailizer."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AddIngredientAmountSerializer(serializers.ModelSerializer):
    """Adding Ingredient and its Amount to the Recipe."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')
    
    def validate(self, attrs):
        if attrs['amount'] < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 1'
            )
        
        return attrs


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Ingredient and its Amount in a Recipe."""

    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
    
    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeListSerializer(serializers.ModelSerializer):
    """List of Recipes Serializer."""
    
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        return IngredientAmountSerializer(
            IngredientAmount.objects.filter(recipe=obj), many=True
        ).data
    
    def get_is_favorited(self, obj):
        user = self.context['request'].user
        recipe = obj
        return Favorite.objects.filter(user=user, recipe=recipe).exists()
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        recipe = obj
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Recipe Serializer."""

    ingredients = AddIngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'ingredients', 'tags',
            'cooking_time', 'pub_date'
        )
        read_only_fields = ('author',)
    

    def create_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            ingredient_pk = ingredient['id']
            ingredient_amount = ingredient['amount']
            IngredientAmount.objects.create(
                ingredient=ingredient_pk,
                recipe=recipe,
                amount=ingredient_amount
            )
    
    def validate(self, attrs):
        if attrs['cooking_time'] < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1'
            )
        
        return attrs

    def add_tags(self, recipe, tags):
        for tag in tags:
            recipe.tags.add(tag)


    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        self.add_tags(recipe, tags)

        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Favorite Serializer."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
    
    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Вы уже добавили данный рецепт в избранное'
            )
        
        return attrs


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Shopping Cart Serializer."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
    
    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Вы уже добавили данный рецепт в корзину'
            )
        
        return attrs
