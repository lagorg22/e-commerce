from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, LogoutSerializer

# User Registration Endpoint
@swagger_auto_schema(
    method='POST',
    operation_summary='Register a New User',
    operation_description='This endpoint allows a new user to register by providing a username, email, and password.',
    request_body=UserRegisterSerializer,
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description='User registered successfully',
            examples={'application/json': {'message': 'User registered successfully'}}
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description='Invalid data provided',
            examples={'application/json': {'username': ['This field is required.']}}
        )
    }
)
@api_view(['POST'])
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Login Endpoint
@swagger_auto_schema(
    method='POST',
    operation_summary='User Login',
    operation_description='This endpoint authenticates a user and returns JWT tokens (access and refresh).',
    request_body=UserLoginSerializer,
    responses={
        status.HTTP_200_OK: openapi.Response(
            description='Login successful',
            examples={'application/json': {'access': 'access_token', 'refresh': 'refresh_token'}}
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description='Invalid credentials',
            examples={'application/json': {'error': 'Invalid credentials'}}
        )
    }
)
@api_view(['POST'])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Profile Endpoint (Protected)
@swagger_auto_schema(
    method='GET',
    operation_summary='Get User Profile',
    operation_description='This endpoint returns the profile of the authenticated user.',
    responses={
        status.HTTP_200_OK: openapi.Response(
            description='User profile retrieved successfully',
            examples={'application/json': {'id': 1, 'username': 'testuser', 'email': 'test@example.com'}}
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description='Authentication credentials were not provided or are invalid.',
            examples={'application/json': {'detail': 'Authentication credentials were not provided.'}}
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# User Logout Endpoint (JWT Blacklist)
@swagger_auto_schema(
    method='POST',
    operation_summary='User Logout',
    operation_description='''
    This endpoint blacklists the refresh token to log out the user.
    You must provide the refresh token that was issued when you logged in.
    After logging out, the token cannot be used to obtain new access tokens.
    ''',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh'],
        properties={
            'refresh': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='The refresh token issued during login'
            )
        }
    ),
    responses={
        status.HTTP_205_RESET_CONTENT: openapi.Response(
            description='Logged out successfully',
            examples={'application/json': {'message': 'Logged out successfully'}}
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description='Invalid refresh token',
            examples={'application/json': {'refresh': ['Invalid token']}}
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description='Authentication required',
            examples={'application/json': {'detail': 'Authentication credentials were not provided.'}}
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout a user by blacklisting their refresh token
    
    To logout, you must provide the refresh token that was issued when you logged in.
    Example request body:
    {
        "refresh": "your_refresh_token_here"
    }
    """
    serializer = LogoutSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(
                {"message": "Logged out successfully"}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
