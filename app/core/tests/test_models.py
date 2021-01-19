from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import User

class UserModelTests(TestCase):
    """Test the user model"""

    def test_user_creation(self):
        """Test the creation of a user"""
        TEST_NAME = 'João Cleber'
        TEST_MAIL = 'joao.cleber@celebridades.net'
        TEST_PASSWORD = 'M0ld3d0r :3'
        TEST_BIO = 'Apresentador João Cleber Fodão 😎'

        # Creating user "João Cleber"
        test_user = User.objects.create_user(name=TEST_NAME, email=TEST_MAIL, password=TEST_PASSWORD, bio=TEST_BIO)

        self.assertTrue(test_user.check_password(TEST_PASSWORD), "Password check assertion")
        self.assertEqual(test_user.get_username(), test_user.email, "Check if the username field is the email")

        # Recovering user by email
        retrieved_user = User.objects.get(email=TEST_MAIL)

        self.assertEqual(retrieved_user, test_user, "Check user retrieval equality")
        self.assertTrue(retrieved_user.check_password(TEST_PASSWORD), "Retrieved user password check assertion")

