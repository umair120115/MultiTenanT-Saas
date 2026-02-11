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
    search_fields = ['name', 'description'] # Allow search by text
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
from .serializers import LeadDetailSerializer
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
class LeadDetailView(APIView):
    # authentication_classes=[TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id=None):
        lead_id = self.kwargs.get('id')
        try:
            lead = Lead.objects.select_related('handler').get(id=lead_id)
            serializer = LeadDetailSerializer(lead)
            return Response(serializer.data, status=200)
        except Lead.DoesNotExist:
            return Response({"detail":"Lead not found!"}, status=404)

    def patch(self, request, id=None):
        lead_id = self.kwargs.get('id')
        try:
            lead = Lead.objects.get_object_or_404(id=lead_id)
            serializer = LeadDetailSerializer(lead, data= request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
        except Lead.DoesNotExist:
            return Response({"detail":"Lead not found!"}, status=404)



from rest_framework.parsers import MultiPartParser
from rest_framework import status, permissions
from .models import TempCSVImport
from .tasks import process_csv_from_db

class CSVUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        
        # 1. Basic Validation
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file_obj.name.endswith('.csv'):
             return Response({"error": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Save file bytes to the Database Buffer
            # This is fast and works perfectly on Render/Docker
            temp_file = TempCSVImport.objects.create(
                file_name=file_obj.name,
                file_content=file_obj.read()  # Reads the file into binary
            )

            # 3. Trigger the Background Task
            # We pass the ID of the temp row and the User ID
            process_csv_from_db.delay(temp_file.id, request.user.id)

            return Response(
                {"message": "File uploaded. Processing started in background."}, 
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# leads/views.py
from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from datetime import timedelta
from .models import Lead

class LeadAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Base Query: All leads for this employee
        qs = Lead.objects.filter(handler=user)

        # 1. Aggregate Global Stats (The heavy lifting)
        stats = qs.aggregate(
            total_leads=Count('id'),
            total_value=Sum('value'),
            
            # Status Counts
            won_count=Count('id', filter=Q(status='success')),
            lost_count=Count('id', filter=Q(status='failure')),
            active_count=Count('id', filter=Q(status='inprogress')),
            
            # Value Counts
            won_value=Sum('value', filter=Q(status='success')),
            pipeline_value=Sum('value', filter=Q(status='inprogress')),
        )

        # 2. "Where do I lag?" - Expiring Soon Logic
        # Leads active but expiring in next 3 days
        three_days_hence = timezone.now().date() + timedelta(days=3)
        expiring_leads = qs.filter(
            status='inprogress', 
            expected_closure_date__lte=three_days_hence,
            expected_closure_date__gte=timezone.now().date()
        ).count()

        # 3. Calculate Win Rate
        total_finished = (stats['won_count'] or 0) + (stats['lost_count'] or 0)
        win_rate = 0
        if total_finished > 0:
            win_rate = (stats['won_count'] / total_finished) * 100

        data = {
            "summary": {
                "total_pipeline_value": stats['pipeline_value'] or 0,
                "total_secured_revenue": stats['won_value'] or 0,
                "win_rate": round(win_rate, 1),
                "total_leads": stats['total_leads']
            },
            "status_breakdown": [
                {"name": "Won", "value": stats['won_count'] or 0, "color": "#4ade80"},
                {"name": "Active", "value": stats['active_count'] or 0, "color": "#d4a373"},
                {"name": "Lost", "value": stats['lost_count'] or 0, "color": "#ef4444"},
            ],
            "action_needed": {
                "expiring_soon_count": expiring_leads
            }
        }
        
        return Response(data)


class LeadNotesView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self, request):
        lead_id = request.data.get('lead')
        note = request.data.get('note')
        if not lead_id or not note:
            return Response({"error":"Lead id or note content is missing!"}, status=400)
        try:
            lead = Lead.objects.get(id=lead_id)
            if request.user != lead.handler :  # currently only for handler can be adjusted as per requirement the authority 
                return Response({"error":"You are not allowed to add notes to this lead!"}, status=403)
            lead.update_notes_leads.create(note=note)
            return Response({"message":"Note added successfully!"}, status=200)

        except Lead.DoesNotExist:
            return Response({"error":"Lead not found!"}, status=404)