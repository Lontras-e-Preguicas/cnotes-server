from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, authentication

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/user/', include('user.urls')),

    path('api/notebook/', include('notebook.urls')),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="CNotes API",
            default_version='v1',
            description="CNotes API docs"
        ),
        authentication_classes=(authentication.TokenAuthentication,),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns.append(path('docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'))

# Media source for FS access
if settings.DEBUG and settings.MEDIA_ROOT:
    urlpatterns.append(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
