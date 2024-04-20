from rest_framework.permissions import BasePermission, SAFE_METHODS


class GetUserPermission(BasePermission):
    def has_permission(self, request, view):
        if 'me' in request.path:
            return request.user.is_authenticated
        return True


class RecieptPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            request.user == obj.author)
