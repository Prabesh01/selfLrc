from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

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


class AddUserForm(forms.Form):
    username = forms.CharField(
        label="username",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'username for New user '})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    def __init__(self, user=None, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)    

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=True
        )        
        try:
            allow_group = Group.objects.get(name='allow')
            user.groups.add(allow_group)
        except Group.DoesNotExist:
            pass
            
        return user
