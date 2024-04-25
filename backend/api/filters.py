from django_filters import rest_framework, filters

from foods.models import Recipt, Favorited, ShoppingCart, Tag
from .utils import filter_generic


class RecipeFilter(rest_framework.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug", queryset=Tag.objects.all())
    is_favorited = rest_framework.BooleanFilter(
        field_name="is_favorited", method="filter_is_favorited")
    is_in_shopping_cart = rest_framework.BooleanFilter(
        field_name="is_in_shopping_cart", method="filter_is_in_shopping_cart")

    class Meta:
        model = Recipt
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")

    def filter_is_favorited(self, queryset, name, value):
        return filter_generic(
            queryset, name, value,
            Favorited, "favorite", "is_favorited", self.request.user
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return filter_generic(
            queryset, name, value,
            ShoppingCart,
            "shopping_cart", "is_in_shopping_cart", self.request.user
        )
