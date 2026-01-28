from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import AuthenticateView , UserOnBoardingView
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='access-token'),
    path('refresh/token/', TokenRefreshView.as_view(), name='refresh-token'),
    path('login/v2/', AuthenticateView.as_view(), name="Authenticate"),
    path('signup/', UserOnBoardingView.as_view(), name="user-onboarding"),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   