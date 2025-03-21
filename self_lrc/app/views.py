from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm, AddUserForm

def get_home(request):
    if not request.user.is_authenticated: return redirect('/admin/login/')
    
    if request.user.is_superuser: 
        site='add_user.html'
        form_f = AddUserForm
        success="User added successfully!"
    else: 
        site='change_passwd.html'
        form_f = CustomPasswordChangeForm
        success="Your password was successfully updated! Login with new credentials!"
    if request.method != 'POST':
        form = form_f(request.user)
        return render(request, site, {'form': form})
    else: 
        form = form_f(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # update_session_auth_hash(request, user)
            messages.success(request, success)
            return redirect('get_home')
        else:
            messages.error(request, 'Please correct the error below.')
            return render(request, site, {'form': form})