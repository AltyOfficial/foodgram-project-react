from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from users.serializers import UserSerializer

from .fields import Base64ImageField


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


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Ingredient and its Amount in a Recipe."""

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class AddIngredientAmountSerializer(serializers.ModelSerializer):
    """Adding Ingredient and its Amount to the Recipe."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1, max_value=10000)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')

    def validate(self, attrs):
        if attrs['amount'] < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 1'
            )

        return attrs


class RecipeListSerializer(serializers.ModelSerializer):
    """List of Recipes Serializer."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('image',)

    def get_ingredients(self, obj):
        return IngredientAmountSerializer(
            IngredientAmount.objects.filter(recipe=obj), many=True
        ).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        recipe = obj
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        recipe = obj
        if user.is_anonymous:
            return False
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

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.add_tags(instance, validated_data.pop('tags'))
        self.create_ingredients(instance, validated_data.pop('ingredients'))
        return super().update(instance, validated_data)


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
