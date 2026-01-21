from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.view import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='access-token'),
    path('refresh/token/', TokenRefreshView.as_view(), name='refresh-token'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   