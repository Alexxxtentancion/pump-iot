from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @staticmethod
    def validate_password(value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        password = validated_data['password']
        user.set_password(password)
        user.save()
        return user

    def update(self, user, validated_data):
        user.username = validated_data.get('username', user.username)
        user.email = validated_data.get('email', user.email)
        password = validated_data.get('password')
        if password:
            user.set_password(password)
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.save()
        return user


class UserTokenSerializer(UserSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        self.token = kwargs.pop('token', None)
        super().__init__(instance, data, **kwargs)

    token = serializers.SerializerMethodField('get_token')

    def get_token(self, data: User):
        if self.token:
            return self.token.key
        if hasattr(data, 'auth_token'):
            return data.auth_token.key

    class Meta:
        model = UserSerializer.Meta.model
        fields = [*UserSerializer.Meta.fields, 'token']


class AuthenticationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
