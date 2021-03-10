from warnings import warn

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions, authentication

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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

urlpatterns = [
    path('admin/', admin.site.urls),

    path('docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),

    path('api/user/', include('user.urls')),
    path('api/notebook/', include('notebook.urls'))
]

# Media source for FS access
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if not settings.DEBUG:
    warn('Registering file system media storage URL outside of DEBUG')
