from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import NoteViewSet

app_name = 'notebook'

main_router = DefaultRouter()

main_router.register('note', NoteViewSet, 'note')

urlpatterns = [
    path('', include(main_router.urls)),
]
