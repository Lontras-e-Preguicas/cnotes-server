from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Notebook, Member, User, Invite

INVITE_URL = reverse('notebook:invite-list')


def create_user_util(**fields):
    data = {
        'email': 'ambrosia@rosie.tucker',
        'name': 'Ambrosia - Rosie Tucker',
        'bio': 'Ambrosia\'s turning me honest',
        'password': '17PBeLUldWC941sX8Ffmkd',
        **fields
    }

    return User.objects.create_user(**data)


class PrivateInviteApiTests(TestCase):
    """Private Note API tests"""
    current_user: User
    notebook: Notebook
    current_user_membership: Member

    def setUp(self):
        self.current_user = create_user_util()
        self.client = APIClient()
        self.client.force_authenticate(user=self.current_user)
        self.target_user = create_user_util(email='wowowowowowo@uwu.exe', name='>:)')
        self.notebook = Notebook.objects.create_notebook(owner=self.current_user, title='Test Notebook')
        self.current_user_membership = Member.objects.get(notebook=self.notebook, user=self.current_user)

    def get_url(self, *args, action='detail'):
        return reverse(f'notebook:invite-{action}', args=args)

    def test_invite_creation(self):
        """Test invite creation"""
        payload = {
            'receiver_email': self.target_user.email,
            'sender_notebook': self.notebook.id
        }

        res = self.client.post(INVITE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        Invite.objects.get(receiver__email=payload['receiver_email'], sender__notebook__id=payload['sender_notebook'])

    def test_invite_accepting(self):
        """Test accepting an invite"""
        test_invite = Invite.objects.create(sender=self.current_user_membership, receiver=self.target_user)

        self.client.force_authenticate(self.target_user)

        res = self.client.post(f'{INVITE_URL}{test_invite.id}/accept/')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Invite.DoesNotExist):
            test_invite.refresh_from_db()

        self.notebook.members.get(user=self.target_user)

    def test_invite_deny(self):
        """Test denying an invite"""
        test_invite = Invite.objects.create(sender=self.current_user_membership, receiver=self.target_user)

        self.client.force_authenticate(self.target_user)

        res = self.client.post(f'{INVITE_URL}{test_invite.id}/deny/')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Invite.DoesNotExist):
            test_invite.refresh_from_db()

        with self.assertRaises(Member.DoesNotExist):
            self.notebook.members.get(user=self.target_user)

    def test_invite_received(self):
        """Test listing received invites"""
        self.client.force_authenticate(self.target_user)

        res = self.client.get(self.get_url('received'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue(isinstance(res.data, list))
        self.assertEqual(len(res.data), 0)

        Invite.objects.create(sender=self.current_user_membership, receiver=self.target_user)

        res = self.client.get(self.get_url('received'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue(isinstance(res.data, list))
        self.assertEqual(len(res.data), 1)

    def test_invite_pending(self):
        """Test listing received invites"""
        res = self.client.get(self.get_url('pending'))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        res = self.client.get(self.get_url('pending') + f'?notebook={self.notebook.id}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue(isinstance(res.data, list))
        self.assertEqual(len(res.data), 0)

        Invite.objects.create(sender=self.current_user_membership, receiver=self.target_user)

        res = self.client.get(self.get_url('pending') + f'?notebook={self.notebook.id}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertTrue(isinstance(res.data, list))
        self.assertEqual(len(res.data), 1)
