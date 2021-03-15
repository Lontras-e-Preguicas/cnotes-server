from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Notebook, Member

# Constants
UserModel = get_user_model()

# Utils


def create_user_util(**fields):
    data = {
        'email': 'aba@gmail.com',
        'name': 'aba',
        'bio': 'auimaue',
        'password': 'abubleabuble',
        **fields
    }

    return UserModel.objects.create_user(**data)


class MemberApiTests(TestCase):
    """Member API tests"""
    current_user: UserModel
    notebook: Notebook
    current_user_membership: Member

    def setUp(self):
        self.current_user = create_user_util()
        self.client = APIClient()
        self.client.force_authenticate(user=self.current_user)

        self.notebook = Notebook.objects.create_notebook(owner=self.current_user, title='Aba Notebook')
        self.current_user_membership = Member.objects.get(notebook=self.notebook, user=self.current_user)

    def detail_url(self, id, namespace):
        return reverse(namespace, args=[id])

    def test_role_change_success(self):
        """Test role change"""
        first_other_user = create_user_util(email='ednaldo@gmail.com')
        first_other_user_membership = Member.objects.create(notebook=self.notebook, user=first_other_user)

        second_other_user = create_user_util(email='ednaldoP@gmail.com')
        second_other_user_membership = Member.objects.create(notebook=self.notebook, user=second_other_user)

        namespace_change = 'notebook:member-change-role'

        # Change a role of a member being the owner
        res = self.client.post(self.detail_url(first_other_user_membership.id,
                                               namespace_change), {'role': Member.Roles.MODERATOR})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        first_other_user_membership.refresh_from_db()
        self.assertEqual(first_other_user_membership.role, Member.Roles.MODERATOR)

        # Change the owner role
        res = self.client.post(self.detail_url(self.current_user_membership.id,
                                               namespace_change), {'role': Member.Roles.MEMBER})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Connecting with a member
        self.client.force_authenticate(second_other_user)

        # Change a role of a member being a member
        res = self.client.post(self.detail_url(first_other_user_membership.id,
                                               namespace_change), {'role': Member.Roles.MEMBER})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Connecting with a moderator
        self.client.force_authenticate(first_other_user)

        # Change a role of a member being a moderator
        res = self.client.post(self.detail_url(second_other_user_membership.id,
                                               namespace_change), {'role': Member.Roles.MODERATOR})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        second_other_user_membership.refresh_from_db()
        self.assertEqual(second_other_user_membership.role, Member.Roles.MODERATOR)

    def test_member_kick_success(self):
        """Test member kick"""
        moderator_user = create_user_util(email='ednaldo@gmail.com')
        moderator_user_membership = Member.objects.create(
            notebook=self.notebook, user=moderator_user, role=Member.Roles.MODERATOR)

        other_user = create_user_util(email='ednaldoP@gmail.com')
        other_user_membership = Member.objects.create(notebook=self.notebook, user=other_user)

        namespace_kick = 'notebook:member-kick-member'

        # Kick the owner
        res = self.client.post(self.detail_url(self.current_user_membership.id, namespace_kick), {'is_active': False})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Connecting with a member
        self.client.force_authenticate(other_user)

        # Kick a member being a member
        res = self.client.post(self.detail_url(moderator_user_membership.id, namespace_kick), {'is_active': False})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Connecting with a moderator
        self.client.force_authenticate(moderator_user)

        # Kick a member being a moderator
        res = self.client.post(self.detail_url(other_user_membership.id, namespace_kick), {'is_active': False})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        other_user_membership.refresh_from_db()
        self.assertEqual(other_user_membership.is_active, False)

        # Connecting with the kicked member
        self.client.force_authenticate(other_user)

        # Kick a member not being a member anymore
        res = self.client.post(self.detail_url(moderator_user_membership.id, namespace_kick), {'is_active': False})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_leave_notebook_success(self):
        """Teste leaving notebook"""
        other_user = create_user_util(email='ednaldoP@gmail.com')
        other_user_membership = Member.objects.create(notebook=self.notebook, user=other_user)

        namespace_leave = 'notebook:member-leave-notebook'

        # Leave notebook being the owner
        res = self.client.post(self.detail_url(self.current_user_membership.id, namespace_leave), {'is_active': False})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Connecting with a member
        self.client.force_authenticate(other_user)

        # Leave notebook being a member
        res = self.client.post(self.detail_url(other_user_membership.id, namespace_leave), {'is_active': False})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        other_user_membership.refresh_from_db()
        self.assertEqual(other_user_membership.is_active, False)

    def test_member_ban_sucess(self):
        """Test member ban"""
        moderator_user = create_user_util(email='ednaldo@gmail.com')
        moderator_user_membership = Member.objects.create(
            notebook=self.notebook, user=moderator_user, role=Member.Roles.MODERATOR)

        other_user = create_user_util(email='ednaldoP@gmail.com')
        other_user_membership = Member.objects.create(notebook=self.notebook, user=other_user)

        namespace_ban = 'notebook:member-ban-member'

        # Ban the owner
        res = self.client.post(self.detail_url(self.current_user_membership.id, namespace_ban), {'is_banned': True})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Connecting with a member
        self.client.force_authenticate(other_user)

        # Ban itself
        res = self.client.post(self.detail_url(other_user_membership.id, namespace_ban), {'is_banned': True})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Ban a member being a member
        res = self.client.post(self.detail_url(moderator_user_membership.id, namespace_ban), {'is_banned': True})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Connecting with a moderator
        self.client.force_authenticate(moderator_user)

        # Ban a member being a moderator
        res = self.client.post(self.detail_url(other_user_membership.id, namespace_ban), {'is_banned': True})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        other_user_membership.refresh_from_db()
        self.assertEqual(other_user_membership.is_banned, True)

        # Connecting with the owner
        self.client.force_authenticate(self.current_user)

        # Ban a member being the owner
        res = self.client.post(self.detail_url(moderator_user_membership.id, namespace_ban), {'is_banned': True})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        moderator_user_membership.refresh_from_db()
        self.assertEqual(moderator_user_membership.is_banned, True)

    def test_member_unban_sucess(self):
        """Test member unban"""
        moderator_user = create_user_util(email='ednaldo@gmail.com')
        Member.objects.create(
            notebook=self.notebook, user=moderator_user, role=Member.Roles.MODERATOR)

        other_user = create_user_util(email='eded@gmail.com')
        Member.objects.create(notebook=self.notebook, user=other_user)

        banned_user = create_user_util(email='ednaldoP@gmail.com')
        banned_user_membership = Member.objects.create(notebook=self.notebook, user=banned_user, is_banned=True)

        namespace_unban = 'notebook:member-unban-member'

        # Connecting with a member
        self.client.force_authenticate(other_user)

        # Unban a member being a member
        res = self.client.post(self.detail_url(banned_user_membership.id, namespace_unban), {'is_banned': False})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Connecting with the owner
        self.client.force_authenticate(self.current_user)

        # Unban a member being the owner
        res = self.client.post(self.detail_url(banned_user_membership.id, namespace_unban), {'is_banned': False})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        banned_user_membership.refresh_from_db()
        self.assertEqual(banned_user_membership.is_banned, False)

        banned_user_membership.is_banned = True
        banned_user_membership.save()

        # Connecting with a moderator
        self.client.force_authenticate(moderator_user)

        # Unban a member being a moderator
        res = self.client.post(self.detail_url(banned_user_membership.id, namespace_unban), {'is_banned': False})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        banned_user_membership.refresh_from_db()
        self.assertEqual(banned_user_membership.is_banned, False)
