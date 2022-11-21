from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name= models.CharField(max_length=200, blank=False, null=False)
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    name= models.CharField(max_length=200, blank=False, null=False)
    color = models.CharField(max_length=7, blank=False, null=False)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
    
    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, related_name='recipes')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes')
    name = models.CharField(max_length=255, blank=False, null=False)
    image = models.ImageField(
        upload_to='recipes/image/',
        null=True,
        default=None
    )
    text = models.TextField(blank=False, null=False)
    cooking_time = models.PositiveSmallIntegerField(blank=False, null=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
    def recipe_favorited_count(self):
        return Favorite.objects.filter(recipe=self).count()
    
    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),)
    )

    class Meta:
        ordering = ['-amount']
        verbose_name = 'Ингредиент и его количество'
        verbose_name_plural = 'Ингредиенты и их количество'
    
    def __str__(self):
        return f'{self.recipe} = {self.ingredient} - {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorited_recipes',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='is_favorited',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт у пользователя'
        verbose_name_plural = 'Избранные рецепт у пользователей'
    
    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='recipes_in_shopping_cart',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='is_in_shopping_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт в корзине у пользователя'
        verbose_name_plural = 'Рецепты в корзине у пользователей'
    
    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}'
