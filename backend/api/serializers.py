import base64

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.core.files.base import ContentFile
from django.db import transaction

from foods.models import (
    CustomUser,
    Tag,
    Recipt,
    Follow,
    Ingredients,
    IngredientsRecipt,
    Favorited,
    ShoppingCart)
from .utils import create_ingredients


class GetUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if (self.context['request'].user.is_authenticated
                and Follow.objects.filter(user=self.context['request'].user,
                                          following=obj).exists()):
            return True
        return False

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id', 'username', 'first_name', 'last_name', 'is_subscribed')
        read_only_fields = fields


class CreateUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')
        read_only_fields = ('id', )


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug'
        )
        read_only_fields = fields


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = (
            'id', 'name', 'measurement_unit'
        )
        read_only_fields = ('name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsRecipt
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageSerializer(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_img, imgstr = data.split(';base64,')
            ext = format_img.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ReciptSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    ingredients = IngredientAmountSerializer(
        source='ingredient_list', many=True)
    author = GetUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        if (self.context['request'].user.is_authenticated
                and Favorited.objects.filter(user=self.context['request'].user,
                                             favorite=obj).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if (self.context['request'].user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=self.context['request'].user,
                    shopping_cart=obj).exists()):
            return True
        return False

    class Meta:
        model = Recipt
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:

        model = IngredientsRecipt
        fields = ('id', 'amount')


class CreateReciptSerializer(serializers.ModelSerializer):
    image = Base64ImageSerializer()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipt
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not ingredients or ingredients is None:
            raise serializers.ValidationError(
                'Нельзя передавать пустые ингредиенты!')
        ingredients_list = [ingredient.get('id') for ingredient in ingredients]
        if (len(set(ingredients_list)) != len(ingredients_list)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными!'
            )
        elif not tags:
            raise serializers.ValidationError(
                'Нужно передать хотя бы один тег!'
            )
        elif len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Теги должны быть уникальными'
            )
        return data

    def to_representation(self, instance):

        serializer = ReciptSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipt.objects.create(**validated_data, author=user)
        recipe.tags.set(tags)
        create_ingredients(
            Ingredients, recipe, IngredientsRecipt, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)

        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            IngredientsRecipt.objects.filter(recipes=instance).delete()
            create_ingredients(
                Ingredients, instance, IngredientsRecipt, ingredients_data)
        return super().update(instance, validated_data)


class ReciptShortSerializer(serializers.ModelSerializer):
    image = Base64ImageSerializer(read_only=True)

    class Meta:
        model = Recipt
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = fields

    def validate(self, data):
        object = self.instance
        user = self.context['request'].user
        path = self.context['request'].path
        if 'favorite' in path:
            if Favorited.objects.filter(
                    user=user.id, favorite=object.id).exists():
                raise serializers.ValidationError(
                    detail='Ты уже добавил в избранное!'
                )
            return data
        elif ShoppingCart.objects.filter(
                user=user.id, shopping_cart=object.id).exists():
            raise serializers.ValidationError(
                detail='Ты уже добавил в корзину!'
            )
        return data


class FollowSerializer(GetUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes_author.count', read_only=True)

    class Meta(GetUserSerializer.Meta):
        fields = GetUserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes_author.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = ReciptShortSerializer(
            recipes, many=True, required=False)
        return serializer.data

    def validate(self, data):
        author = self.instance
        user = self.context['request'].user
        if author == user:
            raise serializers.ValidationError(
                detail='На себя подписываться нельзя!'
            )
        elif Follow.objects.filter(user=user.id, following=author.id).exists():
            raise serializers.ValidationError(
                detail='Ты уже подписан!'
            )
        return data
