from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions, generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserOnBoardingSerializer
# Create your views here.

class AuthenticateView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




class UserOnBoardingView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserOnBoardingSerializer

