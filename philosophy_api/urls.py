from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .auth_views import RegisterView, LoginView
from .views import PingView

# Create a router for viewsets
router = DefaultRouter()
router.register(r'sessions', views.ChatSessionViewSet, basename='session')
router.register(r'philosophers', views.PhilosopherViewSet, basename='philosopher')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('ping/', PingView.as_view(), name='ping'),  # Use the PingView class
]