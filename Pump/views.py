from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError, AuthenticationFailed
from .serializers import RegistrationSerializer, UserSerializer, UserTokenSerializer, AuthenticationSerializer
from .mixins import ResponseSerializerMixin


class RegistrationUserView(ResponseSerializerMixin, APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        form = RegistrationSerializer(data=request.data)
        if not form.is_valid():
            raise ParseError(form.errors)

        with transaction.atomic():
            user = form.save()
            login(request, user)
            token = Token.objects.create(user=user)

        return UserTokenSerializer(user, token=token).data


class LoginView(ResponseSerializerMixin, APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        form = AuthenticationSerializer(data=request.data)
        if not form.is_valid():
            raise ParseError(form.errors)

        user_data = form.validated_data
        user = authenticate(
            username=user_data['username'],
            password=user_data['password']
        )
        if user is None:
            raise AuthenticationFailed

        if not user.is_active:
            raise ParseError('Disabled account')

        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        return UserTokenSerializer(user, token=token).data


class LogoutView(ResponseSerializerMixin, APIView):

    @staticmethod
    def post(request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        logout(request)
