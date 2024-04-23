from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime as dt
from django.db.models import Sum

from foods.models import (
    CustomUser,
    Tag, Recipt,
    Ingredients, Favorited, ShoppingCart, Follow, IngredientsRecipt)
from .serializers import (
    TagsSerializer,
    ReciptSerializer,
    IngredientSerializer,
    CreateReciptSerializer, FollowSerializer, ReciptShortSerializer)
from .permissions import GetUserPermission, RecieptPermission
from .filters import RecipeFilter
from .paginations import FollowPagination
from .utils import create_and_delete_method


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
        methods=['POST', 'DELETE', ], permission_classes=[IsAuthenticated, ])
    def subscribe(self, request, pk):
        return create_and_delete_method(
            request, FollowSerializer, request.user,
            Follow, 'following', pk, 'Такой подписки нет!')


class TagModelViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    http_method_names = ['get', ]
    permission_classes = [GetUserPermission, ]
    pagination_class = None


class ReciptViewSet(ModelViewSet):
    queryset = Recipt.objects.all()
    permission_classes = (RecieptPermission,)
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return CreateReciptSerializer
        return ReciptSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return create_and_delete_method(
            request, ReciptShortSerializer,
            request.user, Favorited, 'favorite', pk, 'Такого в избранном нет!'
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return create_and_delete_method(
            request, ReciptShortSerializer,
            request.user,
            ShoppingCart, 'shopping_cart', pk, 'Такого в корзине нет!')

    @action(
        methods=['GET'],
        detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.in_shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientsRecipt.objects.filter(
            recipes__users_shopping_cart__user=request.user
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
    permission_classes = [GetUserPermission, ]
