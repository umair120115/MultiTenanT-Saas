from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import LeadListCreateView , LeadDetailView, CSVUploadView, LeadAnalyticsView, LeadNotesView

urlpatterns = [
    path('leads/', LeadListCreateView.as_view(), name='lead-list-creator'),
    path('detail/<uuid:id>/', LeadDetailView.as_view(), name='lead-detail' ),
    path('upload-csv/', CSVUploadView.as_view(), name='csv-upload'),
    path('analytics/', LeadAnalyticsView.as_view(), name='lead-analytics'),
    path('notes/', LeadNotesView.as_view(), name= 'lead-notes'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)