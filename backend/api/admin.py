from django.contrib import admin
from django.contrib.auth import get_user_model
from foods.models import (
    Follow,
    Tag, Ingredients, Recipe, Favorited, ShoppingCart, IngredientsRecipe)

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


class IngredientsRecipeInline(admin.TabularInline):
    model = IngredientsRecipe
    min_num = 1
    extra = 1


class ReciptAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'total_favorites',
    )
    list_filter = ('name',)
    list_display_links = ('name',)
    filter_horizontal = ('tags',)
    inlines = [IngredientsRecipeInline]

    def total_favorites(self, obj):
        return Favorited.objects.filter(favorite=obj).count()

    total_favorites.short_description = 'Добавили в избранное'


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
admin.site.register(Tag)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipe, ReciptAdmin)
admin.site.register(Favorited)
admin.site.register(ShoppingCart)
admin.site.register(IngredientsRecipe)
