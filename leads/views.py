from django.shortcuts import render
from rest_framework.views import APIView
from .models import Lead
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

# Create your views here.
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import LeadSerializer
from .filters import LeadFilter
from .pagination import StandardResultsSetPagination

class LeadListCreateView(generics.ListCreateAPIView):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    # 1. Setup Filters
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    filterset_class = LeadFilter
    search_fields = ['name', 'description', 'company__name'] # Allow search by text
    ordering_fields = ['value', 'created_at', 'expected_closure_date']
    ordering = ['-created_at'] # Default ordering

    def get_queryset(self):
        """
        Optimized Queryset to prevent N+1 problems.
        """
        # employee_id = self.kwargs.get('employee_id')
        employee = self.request.user
        if employee:
            return Lead.objects.filter(handler__id=employee.id).select_related('handler')
        # return Lead.objects.all()\
        #     .select_related('company', 'handler') \
        #     .prefetch_related('update_notes') 

    def perform_create(self, serializer):
        # Automatically assign the creator as the handler if needed
        # or simply save the object.
        serializer.save(handler=self.request.user)

from rest_framework.response import Response
class LeadDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        lead_id = self.kwargs.get('lead_id')
        try:
            lead = Lead.objects.select_related('handler').get(id=lead_id)
            serializer = LeadSerializer(lead)
            return Response(serializer.data, status=200)
        except Lead.DoesNotExist:
            return Response({"detail":"Lead not found!"}, status=404)

