from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True, max_length=254, verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Enter a valid slug',
                code='invalid_slug'
            )
        ],
        unique=True,
        verbose_name='Уникальный юзернейм'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=150, verbose_name='Пароль')

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', ]
    USERNAME_FIELD = 'username'


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единици измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    color = models.CharField(
        max_length=7, blank=True, null=True, verbose_name='Цвет')
    slug = models.CharField(
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Enter a valid slug',
                code='invalid_slug'
            )
        ],
        verbose_name='Слаг'
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, related_name='recipes')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes_author')
    ingredients = models.ManyToManyField(
        Ingredients, through='IngredientsRecipe'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Имя')
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            1,
            message='Нужно указать минимум 1'
        )])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class IngredientsRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredient_list',
    )
    amount = models.SmallIntegerField(
        verbose_name='Вес',
        validators=[MinValueValidator(
            1,
            message='Нужно указать минимум 1'
        )]
    )

    def __str__(self) -> str:
        return self.ingredient


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follows'
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='users'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Favorited(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorited'
    )
    favorite = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='users_favorite'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart'
    )
    shopping_cart = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='users_shopping_cart'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
