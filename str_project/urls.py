from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from admin_section.views import ContactUsViewSet

# Router for contact-us
contact_router = DefaultRouter()
contact_router.register('contact-us', ContactUsViewSet, basename='contact-us')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin_section/', include('admin_section.urls')),
    path('api/', include(contact_router.urls)),

    path('api/attendance/', include('attendance.urls')),
    path('api/', include('attendance.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
