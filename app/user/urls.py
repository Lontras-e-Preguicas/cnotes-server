from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreateUserView, CreateAuthTokenView, ManageUserView, PasswordResetViewset

app_name = 'user'

main_router = DefaultRouter()

main_router.register('', PasswordResetViewset, 'password-reset')


urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', CreateAuthTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='me'),
    path('', include(main_router.urls)),
]
