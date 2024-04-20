from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from datetime import datetime as dt
from django.db.models import Sum
from foods.models import (
    CustomUser,
    Tag, Reciept,
    Ingredients, Favorited, ShoppingCart, Follow, IngredientsReciept)

from .serializers import (
    TagsSerializer,
    RecieptSerializer,
    IngredientSerializer,
    CreateRecieptSerializer, FollowSerializer, RecieptShortSerializer)
from .permissions import GetUserPermission, RecieptPermission
from .filters import RecipeFilter
from .paginations import FollowPagination
from .utils import return_400_bad_request, return_201_created


class UserModelViewSet(UserViewSet):
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'pk'

    def get_queryset(self):
        return CustomUser.objects.all()

    @action(detail=False, methods=['GET'], pagination_class=FollowPagination)
    def subscriptions(self, request):
        queryset = self.paginate_queryset(CustomUser.objects.filter(
            users__user=request.user))
        serializer = FollowSerializer(
            queryset, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE',], permission_classes=[IsAuthenticated,])
    def subscribe(self, request, pk):
        user_to_follow = self.get_object()
        if request.method == 'POST':
            serializer = FollowSerializer(
                user_to_follow,
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=request.user, following=user_to_follow)
            return return_201_created(serializer)
        elif request.method == 'DELETE':
            try:
                Follow.objects.get(
                    user=request.user, following=user_to_follow).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return return_400_bad_request('Такой подписки нет!')


class TagModelViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    http_method_names = ['get',]
    permission_classes = [GetUserPermission, ]
    pagination_class = None


class RecieptViewSet(ModelViewSet):
    queryset = Reciept.objects.all()
    permission_classes = (RecieptPermission,)
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return CreateRecieptSerializer
        return RecieptSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        user = request.user
        if request.method == 'POST':
            try:
                reciept = Reciept.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return return_400_bad_request('Такого рецепта нет!')
            serializer = RecieptShortSerializer(
                reciept, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Favorited.objects.create(user=user, favorite=reciept)
            return return_201_created(serializer)
        elif request.method == 'DELETE':
            reciept = self.get_object()
            try:
                Favorited.objects.get(user=user, favorite=reciept).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return return_400_bad_request('Такого в избранном нет!')

    @action(
        methods=['POST', 'DELETE'],
        detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        user = request.user
        if request.method == 'POST':
            try:
                reciept = Reciept.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return return_400_bad_request('Такого рецепта нет!')
            serializer = RecieptShortSerializer(
                reciept, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=user, shopping_cart=reciept)
            return return_201_created(serializer)
        elif request.method == 'DELETE':
            reciept = self.get_object()
            try:
                ShoppingCart.objects.get(
                    user=user, shopping_cart=reciept).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return return_400_bad_request('Такого рецепта тут нет!')

    @action(
        methods=['GET'],
        detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.in_shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientsReciept.objects.filter(
            reciept__users_shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        )
        today = dt.today()
        shopping_list = (
            f'Date: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'| {unit.get("ingredient__name")} '
            f'| ({unit.get("ingredient__measurement_unit")}) '
            f'| {unit.get("amount")}'
            for unit in ingredients
        ])
        shopping_list += f'\n\nFoodgram Inc Corporation ({today:%Y})'
        shopping_list += '\n\nAll terms served'
        filename: str = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ('name',)
    permission_classes = [GetUserPermission,]
