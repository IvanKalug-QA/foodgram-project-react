from rest_framework import status
from rest_framework.response import Response


def return_400_bad_request(massage):
    return Response(
        {'error': massage},
        status=status.HTTP_400_BAD_REQUEST)


def return_201_created(serializer):
    return Response(
        data=serializer.data,
        status=status.HTTP_201_CREATED
    )
