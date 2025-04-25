from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                # Get user data
                user_serializer = UserSerializer(user)
                
                return Response({
                    'user': user_serializer.data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            
            # Format validation errors consistently
            formatted_errors = {}
            for field, errors in serializer.errors.items():
                if field == 'non_field_errors':
                    formatted_errors['detail'] = errors[0] if errors else 'Validation error'
                else:
                    formatted_errors[field] = errors[0] if errors else 'Invalid data'
            
            return Response(formatted_errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                # Get user data
                user_serializer = UserSerializer(user)
                
                return Response({
                    'user': user_serializer.data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)