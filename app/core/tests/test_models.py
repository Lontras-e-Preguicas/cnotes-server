from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import User, Notebook

from datetime import datetime


class UserModelTests(TestCase):
    """Test the user model"""

    def test_user_creation_successful(self):
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

    def test_user_creation_email_normalizing(self):
        """Tests the domain normalization of the email"""
        IN_EMAIL = 'joao.cleber@CElEbriDaDes.net'
        EXPECTED_EMAIL = 'joao.cleber@celebridades.net'

        user = User.objects.create_user(email=IN_EMAIL, name="João Cleber", password="password")
        self.assertEqual(user.email, EXPECTED_EMAIL, "Assert the domain normalization of an email")

    def test_user_creation_invalid_fields(self):
        """Test the required user fields"""
        with self.assertRaises(ValueError, msg="Creating an user with invalid email"):
            User.objects.create_user(email=None, name="Zé Byke", password="password")

        with self.assertRaises(ValueError, msg="Creating an user with invalid name"):
            User.objects.create_user(email="zé@byke.net", name=None, password="password")

        with self.assertRaises(ValueError, msg="Creating an user with no password"):
            User.objects.create_user(email="cuca@beludo.net", name="Cuca Beludo", password=None)


class ModelTests(TestCase):
    """Test the other models"""

    def test_notebook_creation(self):
        """Test the creation of an notebook"""
        TEST_TITLE = 'Notebook 1'

        notebook = Notebook.objects.create(title=TEST_TITLE)
        self.assertEqual(notebook.creation_date.strftime("%D"), datetime.now().strftime("%D"))

        notebook_saved = Notebook.objects.get(id=notebook.id)
        self.assertEqual(notebook_saved.title, TEST_TITLE)
