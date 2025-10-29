# apps/users/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class EmailAuthenticationForm(AuthenticationForm):
    """
    Login form that asks for e-mail instead of username.
    NOTE: the field name must remain 'username' for Django's auth views.
    """
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={"autofocus": True, "placeholder": _("email@example.com")}
        ),
    )

    def clean_username(self):
        # Normalize email to lowercase and trim spaces
        email = self.cleaned_data.get("username", "")
        return (email or "").strip().lower()
