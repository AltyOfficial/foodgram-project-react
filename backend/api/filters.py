from django.db.models import Q
from django_filters import rest_framework as django_filters
from rest_framework import filters

from recipes.models import Recipe, Tag


class IngredientSeatchFilter(filters.SearchFilter):
    search_param = 'name'

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)
        if not search_fields or not search_terms:
            return queryset

        lookup = search_terms[0]

        queryset = queryset.filter(
            Q(name__istartswith=lookup) | Q(name__icontains=lookup)
        )
        return queryset


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        if value is True:
            queryset = queryset.filter(is_favorited__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value is True:
            queryset = queryset.filter(
                is_in_shopping_cart__user=self.request.user)
        return queryset
