from django.contrib.auth.forms import AuthenticationForm
from django import forms

class EmailAuthenticationForm(AuthenticationForm):
    # Переименовываем и тип поля делаем email
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True}),
    )
