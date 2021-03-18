from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User, Activity

ACTIVITY_URL = reverse('notebook:activity-list')


class PrivateActivityApiTests(TestCase):

    def setUp(self):
        self.current_user = User.objects.create_user(email='activity@test.co.uk', name='Activia',
                                                     password='wow-is-it-a-password?')
        self.other_user = User.objects.create_user(email='not.activity@test.co.uk', name='Not Activia',
                                                   password='wow-is-it-not-a-password?')
        self.client = APIClient()
        self.client.force_authenticate(user=self.current_user)

    def detail_url(self, id, action='detail'):
        return reverse(f'notebook:activity-{action}', args=[id])

    def test_activity(self):
        test_activities = [Activity.objects.create(user=self.current_user, title=f'Activity Title {i}',
                                                   description=f'boop the snoot {i + 100} times') for i in range(6)]

        res = self.client.get(ACTIVITY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(res.data, list))
        self.assertEqual(len(test_activities), 6)

        res = self.client.get(self.detail_url(test_activities[0].id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(self.detail_url(test_activities[0].id, 'see'))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        test_activities[0].refresh_from_db()
        self.assertTrue(test_activities[0].seen)

        res = self.client.post(self.detail_url(test_activities[0].id, 'unsee'))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        test_activities[0].refresh_from_db()
        self.assertFalse(test_activities[0].seen)

        self.client.force_authenticate(self.other_user)
        res = self.client.get(self.detail_url(test_activities[0].id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
