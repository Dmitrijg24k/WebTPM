from django import forms

# Reordering Form and View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model=User

class PositionForm(forms.Form):
    position = forms.CharField()