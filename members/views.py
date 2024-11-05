from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


def signup_view(response):
    # check if method is POST
    if response.method == "POST":
        # create a new RegisterForm instance using the data in the request object
        form = RegisterForm(response.POST)
        # check if the form is valid
        if form.is_valid():
            # save the form to create a new User object and redirect to the login page
            form.save()
            messages.success(response, 'Signup successful')
            return redirect('/')
        else:
            # if form is not valid, display an error message
            if form.errors.get('password') and 'Passwords do not match' in form.errors['password']:
                error_msg = 'Passwords do not match. Please try again.'
            else:
                error_msg = 'Form is invalid. Please correct the errors below.'
            return render(response, "signup.html", {"form": form, "error_msg": error_msg})
    else:
        # if method is not POST, create a new instance of the RegisterForm and display the registration page
        form = RegisterForm()
        return render(response, "signup.html", {"form": form})


def login_view(request):
    # check if method is POST
    if request.method == "POST":
        # create a new AuthenticationForm instance using the data in the request object
        form = AuthenticationForm(data=request.POST)
        # check if the form is valid
        if form.is_valid():
            # log in the user and redirect to the RoomList page
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('/')
    else:
        # if method is not POST, create a new instance of the AuthenticationForm and display the login page
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()  # This saves the new password
            update_session_auth_hash(request, user)  # Important: Keeps the user logged in
            messages.success(request, 'Your password has been successfully updated!')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})