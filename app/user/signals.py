from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.dispatch import Signal, receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from core.models import User

password_reset_request_signal = Signal(providing_args=["user"])


@receiver(password_reset_request_signal)
def send_reset_token_email(sender, user: User, *args, **kwargs):
    """
    Handle a password reset request
    """

    token = PasswordResetTokenGenerator().make_token(user)

    context = {
        'name': user.name,
        'uid': user.id,
        'token': token
    }

    text_content = render_to_string('email/password_reset_request.txt', context)
    html_content = render_to_string('email/password_reset_request.html', context)

    msg = EmailMultiAlternatives(
        _("Recuperação de senha"),
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()
