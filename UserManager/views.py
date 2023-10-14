import secrets
import string

import requests
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from UserManager.forms import RegistrationForm, UpdateUserForm
from UserManager.mikrotik import hotspot_profiles
from UserManager.models import Registration
from UserManager.tasks import scheduler


def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Check if a user with the same email already exists
            email = form.cleaned_data['email']
            if Registration.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
            else:
                # Save the registration details to the database
                form.save()
                return redirect('registration_success')
        else:
            messages.error(request, "Please correct the errors in the form.", extra_tags="danger")
    else:
        form = RegistrationForm()

    return render(request, 'user_manager/registration.html', {'form': form})


def registration_success(request):
    return render(request, 'user_manager/registration_success.html')


def manage_users(request):
    users = Registration.objects.all()
    return render(request, 'user_manager/manage_users.html', {'users': users})


def edit_user(request, user_id):
    user = get_object_or_404(Registration, pk=user_id)
    return render(request, 'user_manager/edit_user.html', {'user': user, 'profiles': hotspot_profiles})


def update_user(request, user_id):
    user = get_object_or_404(Registration, pk=user_id)
    old_email = user.email  # Get the old email from the user instance

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)  # Provide instance=user here
        if form.is_valid():
            new_email = form.cleaned_data['email']  # Get the new email from the form
            new_profile = form.cleaned_data['profile']  # Get the new user profile

            if new_email != old_email:
                # Email was changed, so check if the new email is unique
                if Registration.objects.exclude(id=user_id).filter(email=new_email).exists():
                    messages.error(request, "The new email is already in use.", extra_tags="danger")
                    return redirect('edit_user', user_id=user_id)

            user.profile = new_profile  # Set user profile
            form.save()  # Update the user instance with the new data
            messages.success(request, "User details updated successfully.")
            return redirect('manage_users')
    else:
        form = UpdateUserForm(instance=user)
    return render(request, 'user_manager/edit_user.html', {'user': user, 'form': form, 'profiles': hotspot_profiles})


# Function to toggle enabling and disabling user account
# if toggled to enable the user is added to the list of users that will receive notification
# and their details populated in the radius database
def toggle_enable_user(request, user_id):
    user = get_object_or_404(Registration, pk=user_id)

    if request.method == 'POST':
        if user.profile is None:
            messages.error(request, "You can only enable a user with a set profile. Edit the user's profile first.",
                           extra_tags="danger")
            return redirect('manage_users')

        if user.is_enabled:
            # Disable the user
            user.is_enabled = False
            user.save()
            messages.success(request, "User disabled successfully.")
        else:
            # Enable the user and generate a password if it's empty
            if not user.password:
                # Generate a random password
                password = generate_random_password(8)
                user.password = password
            user.is_enabled = True
            user.save()
            messages.success(request, "User enabled successfully and password set.")

    return redirect('manage_users')


def login_to_mikrotik(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        hotspot_url = '192.168.56.128'

        # Replace with your MikroTik Hotspot API endpoint
        hotspot_api_url = f"https://{hotspot_url}/login"

        # Replace with the appropriate parameters for MikroTik login
        params = {
            "username": username,
            "password": password,
        }

        response = requests.post(hotspot_api_url, data=params)

        if response.status_code == 200:
            # Successful login, redirect to the previous page or Google
            return redirect(request.META.get('HTTP_REFERER', 'https://www.google.com'))
        else:
            # Failed login, show a message to the user
            messages.error(request, "Login failed. Please check your credentials.", extra_tags="danger")
            return redirect("login")

    return render(request, "user_manager/login.html")


if not scheduler.running:
    scheduler.start()
