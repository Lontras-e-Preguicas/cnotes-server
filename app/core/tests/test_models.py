from django.test import TestCase
from core.models import User, Notebook, Folder, NoteGroup, Member, Invite, Activity, Note, Rating, Comment
from django.db.utils import IntegrityError

from datetime import datetime


# Test utils.py
def create_test_user(
    name='João Cleber',
    mail='joao.cleber@celebridades.net',
    password='M0ld3d0r :3',
    bio='Apresentador João Cleber Fodão 😎'
) -> User:
    """Create an user for testing"""

    return User.objects.create_user(name=name, email=mail, password=password, bio=bio)


def create_test_notebook(user: User) -> Notebook:
    """Create a notebook for testing"""
    return Notebook.objects.create(title="Test Notebook", owner=user)


def create_test_folder(notebook: Notebook, parent_folder: Folder = None) -> Folder:
    """Create a folder for testing"""
    return Folder.objects.create(title='Test Folder', notebook=notebook, parent_folder=parent_folder)


def create_test_member(user: User, notebook: Notebook) -> Member:
    """Create a member for testing"""
    return Member.objects.create(user=user, notebook=notebook)


def create_test_invite(member: Member, user: User) -> Invite:
    """Create an invite for testing"""
    return Invite.objects.create(member=member, user=user)


def create_test_activity(user: User, title: str, description: str) -> Activity:
    """Create an activity for testing"""
    return Activity.objects.create(user=user, title=title, description=description)


def create_test_note_group(parent_folder: Folder, title: str = 'Test NoteGroup') -> NoteGroup:
    return NoteGroup.objects.create(title=title, parent_folder=parent_folder)


def create_test_note(author: Member, note_group: NoteGroup, title: str = "Test Note") -> Note:
    """Create a note for testing"""
    return Note.objects.create(author=author, note_group=note_group, title=title)


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
        self.assertEqual(notebook.creation_date.strftime("%D"), datetime.utcnow().strftime("%D"))

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

    # Member Tests

    def teste_member_creation(self):
        """Test the creation of a member"""
        test_user = create_test_user()
        test_owner = create_test_user(name='Ednaldo Pereira', mail='ednaldo@gmail.com', password='abuble', bio='brabo')
        test_notebook = create_test_notebook(test_owner)

        member = Member.objects.create(user=test_user, notebook=test_notebook)
        self.assertEqual(member.user, test_user)
        self.assertEqual(member.notebook, test_notebook)
        self.assertEqual(member.member_since.strftime("%D"), datetime.utcnow().strftime("%D"))

    # Invite Test

    def test_invite_creation(self):
        """Test the creation of an invite"""
        # Criação do dono do caderno e do caderno para criar um membro
        test_owner = create_test_user(name='Ednaldo', mail='ed@gmail.com', password='abuble', bio='gente boa')
        test_notebook = create_test_notebook(test_owner)
        # Criação do membro que irá enviar o convite
        test_member = create_test_member(test_owner, test_notebook)
        # Criação do usuário que irá receber o convite
        test_user = create_test_user()

        invite = Invite.objects.create(sender=test_member, receiver=test_user)
        self.assertEqual(invite.sender, test_member)
        self.assertEqual(invite.receiver, test_user)
        self.assertEqual(invite.invite_date.strftime("%D"), datetime.utcnow().strftime("%D"))

    # Activity Test

    def test_activity_creation(self):
        """Test the creation of an activity"""
        test_user = create_test_user()
        test_title = 'Atividade Teste'
        test_description = 'Essa atividade foi criada para fins de teste'

        activity = Activity.objects.create(user=test_user, title=test_title, description=test_description)
        self.assertEqual(activity.user, test_user)
        self.assertEqual(activity.description, test_description)
        self.assertEqual(activity.title, test_title)

    # Note Test

    def test_note_creation(self):
        """Test the creation of a note"""
        test_user = create_test_user()
        test_notebook = create_test_notebook(test_user)
        test_member = create_test_member(test_user, test_notebook)
        test_folder = create_test_folder(test_notebook)
        test_note_group = create_test_note_group(test_folder)

        test_title = "Some Note"

        test_note = Note.objects.create(author=test_member, note_group=test_note_group, title=test_title)
        self.assertEqual(test_note.author, test_member)
        self.assertEqual(test_note.creation_date.strftime("%D"), datetime.utcnow().strftime("%D"))
        self.assertEqual(test_note.title, test_title)
        self.assertEqual(test_note.content, "")

        self.assertIn(test_note, test_note_group.notes.all())
        self.assertIn(test_note, test_member.notes.all())
        self.assertIsNotNone(str(test_note))

    def test_rating_creation(self):
        """Test the creation of a rating"""
        test_user = create_test_user()
        test_notebook = create_test_notebook(test_user)
        test_member = create_test_member(test_user, test_notebook)
        test_folder = create_test_folder(test_notebook)
        test_note_group = create_test_note_group(test_folder)
        test_note = create_test_note(test_member, test_note_group)

        test_rating = Rating.objects.create(note=test_note, rating=8, rater=test_member)

        self.assertIsNotNone(str(test_rating))
        self.assertIn(test_rating, test_note.ratings.all())
        self.assertEqual(test_rating.rating, 8)
        self.assertIn(test_rating, test_member.rates.all())
        self.assertEqual(test_rating.rated_date.strftime("%D"), datetime.utcnow().strftime("%D"))

        with self.assertRaises(IntegrityError):
            Rating.objects.create(note=test_note, rating=8, rater=test_member)

    def test_comment_creation(self):
        """Test comment creation"""
        test_user = create_test_user()
        test_notebook = create_test_notebook(test_user)
        test_member = create_test_member(test_user, test_notebook)
        test_folder = create_test_folder(test_notebook)
        test_note_group = create_test_note_group(test_folder)
        test_note = create_test_note(test_member, test_note_group)

        test_comment = Comment.objects.create(note=test_note, commenter=test_member, message="Test comment")

        self.assertIsNotNone(str(test_comment))
        self.assertIn(test_comment, test_note.comments.all())
        self.assertIn(test_comment, test_member.comments.all())
        self.assertFalse(test_comment.solved)
        self.assertEqual(test_comment.creation_date.strftime("%D"), datetime.utcnow().strftime("%D"))

    def test_notebook_create_notebook(self):
        """Test the custom create_notebook method"""
        test_user = create_test_user()

        test_notebook: Notebook = Notebook.objects.create_notebook(title="Test title", owner=test_user)

        self.assertIsNotNone(test_notebook.id)

        Notebook.objects.get(id=test_notebook.id)  # If not found, raises exception

        membership = Member.objects.get(notebook=test_notebook, user=test_user)  # If not found, raises exception

        self.assertEqual(membership.role, Member.Roles.ADMIN)  # Assert right role assignment

        Folder.objects.get(notebook=test_notebook, parent_folder=None)  # If root folder not found, raises exception
