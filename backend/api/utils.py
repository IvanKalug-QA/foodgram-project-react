from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef

from foods.models import Recipt

User = get_user_model()


def return_400_bad_request(massage):
    return Response(
        {'error': massage},
        status=status.HTTP_400_BAD_REQUEST)


def return_201_created(serializer):
    return Response(
        data=serializer.data,
        status=status.HTTP_201_CREATED
    )


def create_ingredients(model,
                       recipe, many_to_many_ingredients_model, ingredients):
    ingredients_objs = list()
    for ingredient in ingredients:
        id = ingredient['id']
        amount = ingredient['amount']
        try:
            current_ingredient = model.objects.get(id=id)
            ingredients_objs.append(many_to_many_ingredients_model(
                ingredient=current_ingredient,
                recipes=recipe,
                amount=amount)
            )
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'Несуществующие ингредиент!'
            )
    many_to_many_ingredients_model.objects.bulk_create(ingredients_objs)


def create_and_delete_method(request,
                             serializator, user, model, field_name, pk):
    if request.method == 'POST':
        if 'subscribe' in request.path:
            obj = get_object_or_404(User, pk=pk)
        else:
            try:
                obj = Recipt.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return return_400_bad_request('Такого рецепта нет!')
        serializer = serializator(
            obj,
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        model.objects.create(user=user, **{field_name: obj})
        return return_201_created(serializer)
    elif request.method == 'DELETE':
        if 'subscribe' in request.path:
            obj = get_object_or_404(User, pk=pk)
        else:
            obj = get_object_or_404(Recipt, pk=pk)
        try:
            model.objects.get(
                user=user, **{field_name: obj}).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return return_400_bad_request('Такой подписки нет!')


def filter_generic(queryset, name,
                   value, related_model, related_field, field_in_recipt, user):
    if user.is_authenticated:
        if value:
            return queryset.annotate(
                field_in_recipt=Exists(
                    related_model.objects.filter(
                        user=user, **{related_field: OuterRef("pk")}
                    )
                )
            ).filter(field_in_recipt=True)
        else:
            return queryset.exclude(
                **{f"users_{related_field}__user": user})
    else:
        return queryset.none()
