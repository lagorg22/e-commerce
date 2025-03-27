from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        # Regular users are created with is_staff=False by default
        user = User.objects.create_user(**validated_data)
        return user


class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        # Create an admin user with is_staff=True
        user = User.objects.create_user(**validated_data)
        user.is_staff = True
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(source='is_staff', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_admin']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
    
    default_error_messages = {
        'bad_token': 'Token is invalid or expired',
        'blacklisted': 'Token has already been blacklisted'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            # Try to blacklist the token
            RefreshToken(self.token).blacklist()
        except TokenError:
            # If the token is invalid or expired
            self.fail('bad_token')
