from rest_framework import status, generics, permissions
from rest_framework.response import Response

from mailme.api.serializers.auth import RegisterSerializer, JWTSerializer, LoginSerializer
from mailme.utils.jwt import encode_token


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

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


class LoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def get_response_serializer(self):
        return JWTSerializer

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        # Login the user
        user = self.serializer.validated_data['user']
        token = encode_token(user.id)

        data = {
            'user': user,
            'token': token
        }
        serializer = JWTSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)
