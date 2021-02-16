from django.test import TestCase
from core.models import User, Notebook, Folder, NoteGroup

from datetime import datetime


# Test utils
def create_test_user() -> User:
    """Create an user for testing"""
    test_name = 'João Cleber'
    test_mail = 'joao.cleber@celebridades.net'
    test_password = 'M0ld3d0r :3'
    test_bio = 'Apresentador João Cleber Fodão 😎'

    return User.objects.create_user(name=test_name, email=test_mail, password=test_password, bio=test_bio)


def create_test_notebook(user: User) -> Notebook:
    """Create a notebook for testing"""
    return Notebook.objects.create(title="Test Notebook", owner=user)


def create_test_folder(notebook: Notebook, parent_folder: Folder = None) -> Folder:
    """Create a folder for testing"""
    return Folder.objects.create(title='Test Folder', notebook=notebook, parent_folder=parent_folder)


class ModelTests(TestCase):
    """Test the models"""

    # User tests

    def test_user_creation_successful(self):
        """Test the creation of a user"""
        test_name = 'João Cleber'
        test_mail = 'joao.cleber@celebridades.net'
        test_password = 'M0ld3d0r :3'
        test_bio = 'Apresentador João Cleber Fodão 😎'

        # Creating user "João Cleber"
        test_user = User.objects.create_user(name=test_name, email=test_mail, password=test_password, bio=test_bio)

        self.assertTrue(test_user.check_password(test_password), "Password check assertion")
        self.assertEqual(test_user.get_username(), test_user.email, "Check if the username field is the email")

        # Recovering user by email
        retrieved_user = User.objects.get(email=test_mail)

        self.assertEqual(retrieved_user, test_user, "Check user retrieval equality")
        self.assertTrue(retrieved_user.check_password(test_password), "Retrieved user password check assertion")

    def test_user_creation_email_normalizing(self):
        """Tests the domain normalization of the email"""
        in_email = 'joao.cleber@CElEbriDaDes.net'
        expected_email = 'joao.cleber@celebridades.net'

        user = User.objects.create_user(email=in_email, name="João Cleber", password="password")
        self.assertEqual(user.email, expected_email, "Assert the domain normalization of an email")

    def test_user_creation_invalid_fields(self):
        """Test the required user fields"""
        with self.assertRaises(ValueError, msg="Creating an user with invalid email"):
            User.objects.create_user(email=None, name="Zé Byke", password="password")

        with self.assertRaises(ValueError, msg="Creating an user with invalid name"):
            User.objects.create_user(email="zé@byke.net", name=None, password="password")

        with self.assertRaises(ValueError, msg="Creating an user with no password"):
            User.objects.create_user(email="cuca@beludo.net", name="Cuca Beludo", password=None)

    # Notebook Tests

    def test_notebook_creation(self):
        """Test the creation of a notebook"""
        test_user = create_test_user()

        test_title = 'Notebook 1'

        notebook = Notebook.objects.create(title=test_title, owner=test_user)
        self.assertEqual(notebook.creation_date.strftime("%D"), datetime.now().strftime("%D"))

        notebook_saved = Notebook.objects.get(id=notebook.id)
        self.assertEqual(notebook_saved.title, test_title)
        self.assertEqual(notebook_saved.owner_id, test_user.id)

        self.assertEqual(str(notebook), test_title)

    def test_folder_creation(self):
        """Test the creation of a Folder"""
        test_user = create_test_user()

        test_notebook = create_test_notebook(test_user)

        root_folder_title = 'Anxiety'
        sub_folder_title = 'Peace'

        root_folder = Folder.objects.create(title=root_folder_title, notebook=test_notebook, parent_folder=None)
        self.assertEqual(root_folder.parent_folder, None)
        self.assertEqual(root_folder.notebook_id, test_notebook.id)
        self.assertEqual(root_folder.title, root_folder_title)

        sub_folder = Folder.objects.create(title=sub_folder_title, notebook=test_notebook, parent_folder=root_folder)
        self.assertEqual(sub_folder.parent_folder_id, root_folder.id)
        self.assertEqual(sub_folder.notebook_id, sub_folder.parent_folder.notebook_id)

        root_folder.refresh_from_db()
        sub_folders = root_folder.sub_folders.all()
        self.assertIn(sub_folder, sub_folders)

    def test_note_group_creation(self):
        """Test the creation of a NoteGroup"""
        test_user = create_test_user()
        test_notebook = create_test_notebook(test_user)
        test_folder = create_test_folder(test_notebook)

        test_title = 'Test Note Group'

        note_group = NoteGroup.objects.create(title=test_title, parent_folder=test_folder)
        self.assertEqual(note_group.title, test_title)
        self.assertEqual(note_group.parent_folder_id, test_folder.id)

        folders_groups = test_folder.note_groups.all()
        self.assertIn(note_group, folders_groups)
