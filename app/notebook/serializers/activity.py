from rest_framework import serializers

from core.models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('id', 'title', 'description', 'seen', 'creation_date')
        read_only_fields = ('title', 'description')
