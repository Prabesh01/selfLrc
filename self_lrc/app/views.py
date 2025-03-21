from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm

def get_home(request):
    if not request.user.is_authenticated: return redirect('/admin/login/')
    if request.method != 'POST':
        form = CustomPasswordChangeForm(request.user)
        return render(request, 'change_passwd.html', {'form': form})
    else: 
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated! Login with new credentials!')
            return redirect('get_home')
        else:
            messages.error(request, 'Please correct the error below.')
            return render(request, 'change_passwd.html', {'form': form})