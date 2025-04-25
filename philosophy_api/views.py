# Fix the authentication issue in the views.py file

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .groq_client_django import GroqClient
from datetime import datetime
import uuid
import logging
import json
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.views import APIView

# Import the philosophers module
from philosophers import PHILOSOPHERS, get_all_philosophers

# Configure logging
logger = logging.getLogger(__name__)

User = get_user_model()

class PhilosopherViewSet(viewsets.ViewSet):
    """ViewSet for retrieving philosopher information"""
    permission_classes = [AllowAny]  # Allow anyone to view philosophers
    
    def list(self, request):
        """List all available philosophers"""
        philosophers = get_all_philosophers()
        return Response(philosophers)
    
    def retrieve(self, request, pk=None):
        """Retrieve a specific philosopher by ID"""
        philosopher = PHILOSOPHERS.get(pk)
        if not philosopher:
            return Response({'error': 'Philosopher not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'id': pk,
            'name': philosopher['name'],
            'avatar': philosopher['avatar']
        })

# Update the ChatSessionViewSet to require authentication
class ChatSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for chat sessions"""
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]  # Require authentication
    
    def get_queryset(self):
        """Filter sessions by user"""
        user = self.request.user
        return ChatSession.objects.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """Create a new chat session"""
        try:
            # Log the authentication status to help debug
            logger.info(f"User authenticated: {request.user.is_authenticated}")
            logger.info(f"User: {request.user}")
            
            philosopher_id = request.data.get('philosopher', 'marcus_aurelius')
            
            # Check if philosopher exists
            if philosopher_id not in PHILOSOPHERS:
                return Response({'error': f'Philosopher {philosopher_id} not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create a unique session ID
            session_id = str(uuid.uuid4())
            
            # Create the session
            session = ChatSession.objects.create(
                session_id=session_id,
                philosopher=philosopher_id,
                user=request.user
            )
            
            serializer = self.get_serializer(session)
            response_data = serializer.data
            # Ensure the id is included in the response
            response_data['id'] = str(session.id)
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """Add a message to a chat session and get AI response"""
        try:
            session = self.get_object()
            user_message = request.data.get('message', '')
            
            if not user_message:
                return Response({'error': 'No message provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save user message to database
            ChatMessage.objects.create(
                session=session,
                role='user',
                content=user_message
            )
            
            # Get all messages for this session
            messages = []
            
            # Add system message first
            try:
                philosopher = PHILOSOPHERS[session.philosopher]
                messages.append({'role': 'system', 'content': philosopher['system_message']})
            except KeyError:
                # Fallback if philosopher not found
                messages.append({'role': 'system', 'content': 'You are a wise philosopher.'})
                logger.error(f"Philosopher {session.philosopher} not found in PHILOSOPHERS dictionary")
            
            # Add all previous messages
            db_messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
            for msg in db_messages:
                messages.append({'role': msg.role, 'content': msg.content})
            
            # Get AI response
            try:
                groq_client = GroqClient()
                response = groq_client.generate_response(messages)
                
                # Save AI response to database
                ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=response
                )
                
                # Update session timestamp
                session.updated_at = datetime.now()
                session.save()
                
                return Response({
                    'response': response,
                    'session_id': session.session_id
                })
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                return Response({
                    'error': f"Error generating response: {str(e)}",
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in add_message: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['patch'], url_path='change-philosopher')
    def change_philosopher(self, request, pk=None):
        """Change philosopher for an existing chat session"""
        try:
            session = self.get_object()
            new_philosopher = request.data.get('philosopher')
            
            if not new_philosopher:
                return Response({'error': 'No philosopher specified'}, status=status.HTTP_400_BAD_REQUEST)
            
            if new_philosopher not in PHILOSOPHERS:
                return Response({'error': f'Philosopher {new_philosopher} not found'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            session.philosopher = new_philosopher
            session.save()
            
            # Update system message in existing messages
            ChatMessage.objects.filter(session=session, role='system').delete()
            ChatMessage.objects.create(
                session=session,
                role='system',
                content=PHILOSOPHERS[new_philosopher]['system_message']
            )
            
            return Response(self.get_serializer(session).data)
            
        except Exception as e:
            logger.error(f"Error changing philosopher: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Add this new view class at the top level of the file
class PingView(APIView):
    """Simple health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({'status': 'ok'})