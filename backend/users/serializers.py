from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers

from recipes.models import Recipe

from .models import Subscribtion


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        user_to_subscribe = obj.id
        if current_user.is_anonymous:
            return False
        flag = Subscribtion.objects.filter(
            user=current_user, author=user_to_subscribe
        ).exists()

        return flag

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscribtion Serializer."""

    class Meta:
        model = Subscribtion
        fields = ('user', 'author')

    def validate(self, attrs):
        user = attrs['user']
        user_to_subscribe = attrs['author']

        if user == user_to_subscribe:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )

        if Subscribtion.objects.filter(
            user=user, author=user_to_subscribe
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя.'
            )

        return attrs


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Short Recipe Descriotion For User's Subscribing List."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionListSerializer(UserSerializer):
    "List Of Subscribed Users."

    # recipes = ShortRecipeSerializer(many=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        num = int(self.context['request'].query_params['recipes_limit'])
        queryset = Recipe.objects.all()[:num]
        list = ShortRecipeSerializer(queryset, many=True).data
        return list

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value
