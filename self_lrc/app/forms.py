from django import forms
from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )