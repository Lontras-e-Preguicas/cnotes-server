from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import serializers, exceptions

from core.models import Notebook, Member, User

class NotebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook
        fields = ('id', 'title','creation_date','owner' )