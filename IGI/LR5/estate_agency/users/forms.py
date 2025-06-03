import logging
from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Client
from .utils import RestrictedAgeValidator
from .validators import phone_regex

logger = logging.getLogger(__name__)


class ClientSignUpForm(UserCreationForm):
    phone_number = forms.CharField(
        validators=[phone_regex],
        max_length=17,
        required=False,
        help_text=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    birth_date = forms.DateField(
        required=False,
        help_text=_("Enter your birth date")
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'birth_date', 'password1', 'password2')

    def save(self, commit=True):
        logger.debug(
            f"Preparing to save user with username: {self.cleaned_data.get('username')}"
        )
        try:
            user = super().save(commit=False)
            user.role = "client"
            user.last_name = self.cleaned_data["last_name"]
            if commit:
                user.save()
                logger.info(f"User saved: {user.username}, role: {user.role}")
                Client.objects.create(
                    user=user,
                    phone_number=self.cleaned_data.get('phone_number'),
                    birth_date=self.cleaned_data.get('birth_date')
                )
                logger.info(f"Client created for user: {user.username}")
            return user
        except Exception:
            logger.exception(
                f"Error saving user {self.cleaned_data.get('username')} or creating Client:"
            )
            raise
