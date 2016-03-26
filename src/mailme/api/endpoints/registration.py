from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from mailme.api.serializers.auth import RegisterSerializer, JWTSerializer
from mailme.utils.jwt import encode_token


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data = {
            'user': user,
            'token': encode_token(user.id)
        }
        return Response(
            JWTSerializer(data).data,
            status=status.HTTP_201_CREATED,
            headers=headers)
