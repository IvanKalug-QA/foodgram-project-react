from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    UserModelViewSet, ReciptViewSet, TagModelViewSet, IngredientsViewSet)

router = SimpleRouter()

router.register('users', UserModelViewSet, basename='users')
router.register('recipes', ReciptViewSet)
router.register('tags', TagModelViewSet)
router.register('ingredients', IngredientsViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
