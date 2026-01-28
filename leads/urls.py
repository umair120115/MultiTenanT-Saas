from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import LeadListCreateView , LeadDetailView, CSVUploadView

urlpatterns = [
    path('leads/', LeadListCreateView.as_view(), name='lead-list-creator'),
    path('detail/<uuid:lead_id>/', LeadDetailView.as_view(), name='lead-detail' ),
    path('upload-csv/', CSVUploadView.as_view(), name='csv-upload'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)