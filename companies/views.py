from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.core.cache import cache
# Create your views here.
from .models import Company
from rest_framework.pagination import PageNumberPagination
from .serializers import CompanySerializer
class CompanyAdminPagination(PageNumberPagination):
    page_size=20
    page_size_query_param='page_size'
    max_page_size=100

class CompanyListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    pagination_class = CompanyAdminPagination

