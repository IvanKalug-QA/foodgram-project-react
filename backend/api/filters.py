import django_filters
from django_filters import rest_framework as rest_framework_filters
from django.db.models import Exists
from django.db.models import OuterRef

from foods.models import Reciept, Favorited, ShoppingCart, Tag


class RecipeFilter(rest_framework_filters.FilterSet):
    tags = django_filters.filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug", queryset=Tag.objects.all())
    is_favorited = rest_framework_filters.BooleanFilter(
        field_name="is_favorited", method="filter_is_favorited")
    is_in_shopping_cart = rest_framework_filters.BooleanFilter(
        field_name="is_in_shopping_cart", method="filter_is_in_shopping_cart")

    class Meta:
        model = Reciept
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.annotate(
                    is_favorited=Exists(
                        Favorited.objects.filter(
                            user=user, favorite=OuterRef("pk"))
                    )
                ).filter(is_favorited=True)
            else:
                return queryset.exclude(
                    users_favorite__user=user
                )
        else:
            return queryset.none()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.annotate(
                    is_in_shopping_cart=Exists(
                        ShoppingCart.objects.filter(
                            user=user, shopping_cart=OuterRef("pk"))
                    )
                ).filter(is_in_shopping_cart=True)
            else:
                return queryset.exclude(
                    users_shopping_cart__user=user
                )
        else:
            return queryset.none()
