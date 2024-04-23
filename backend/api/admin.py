from django.contrib import admin
from django.contrib.auth import get_user_model
from foods.models import (
    Follow,
    Tag, Ingredients, Recipt, Favorited, ShoppingCart, IngredientsRecipt)

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username',)
    list_display_links = ('username',)


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    list_display_links = ('name',)


class ReciptAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'total_favorites',
    )
    list_filter = ('name',)
    list_display_links = ('name',)
    filter_horizontal = ('tags', 'ingredients')

    def total_favorites(self, obj):
        return Favorited.objects.filter(favorite=obj).count()

    total_favorites.short_description = 'Добавили в избранное'


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
admin.site.register(Tag)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipt, ReciptAdmin)
admin.site.register(Favorited)
admin.site.register(ShoppingCart)
admin.site.register(IngredientsRecipt)
