from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from core.models import Member, Rating


class RatingSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(source='note.avg_rating', read_only=True)

    class Meta:
        model = Rating
        fields = ('note', 'rating', 'rated_date', 'avg_rating')
        read_only_fields = ('rated_date',)

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(_('A avaliação deve estar entre 1 e 5'))
        return value

    def validate(self, attrs):
        if self.instance:
            note = self.instance.note
            if 'note' in attrs:
                if attrs['note'] != self.instance.note:
                    raise serializers.ValidationError(_('Não é possível transferir uma anotação entre usuários'))
        else:
            note = attrs['note']

        if not self.instance:
            try:
                rater = note.notebook.members.get(user=self.context['request'].user, is_active=True)
                attrs['rater'] = rater
            except Member.DoesNotExist:
                raise serializers.ValidationError(_('O usuário não é membro do caderno'))

        return attrs
