import random
import secrets
import string

import requests
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render

from UserManager.forms import UserInfoForm, UpdateUserInfoForm
from UserManager.mikrotik import hotspot_profiles
from UserManager.tasks import scheduler
from .models import UserInfo


def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_username(first_name, last_name):
    # Take the first three characters of the first name and last name
    first_name_part = first_name[:1].lower()
    last_name_part = last_name.lower()

    # Generate a unique username based on the selected parts and a random alphanumeric value
    alphanumeric_value = ''.join(random.choices(string.digits, k=2))
    return f"{first_name_part}{last_name_part}{alphanumeric_value}"


@transaction.atomic
def registration(request):
    if request.method == "POST":
        form = UserInfoForm(request.POST)
        if form.is_valid():
            # Check if a user with the same email already exists
            email = form.cleaned_data['email']
            if UserInfo.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
            else:
                # Save the registration details to the database
                form.save()
                return redirect('registration_success')
        else:
            messages.error(request, "Please correct the errors in the form.", extra_tags="danger")
    else:
        form = UserInfoForm()

    return render(request, 'user_manager/registration.html', {'form': form})


def registration_success(request):
    return render(request, 'user_manager/registration_success.html')


def manage_users(request):
    # Get the current page number from the request
    page = request.GET.get('page')

    # Set the number of items to display per page
    items_per_page = 10

    # Create a Paginator object for the Registration model
    paginator = Paginator(UserInfo.objects.all().order_by('firstname'), items_per_page)

    # Ensure the page parameter is a valid integer
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1

    # Get the Page object for the current page
    users = paginator.get_page(page)

    return render(request, 'user_manager/manage_users.html', {
        'users': users,
    })


def edit_user(request, user_id):
    user = get_object_or_404(UserInfo, pk=user_id)
    return render(request, 'user_manager/edit_user.html', {'user': user, 'profiles': hotspot_profiles})


@transaction.atomic
def update_user(request, user_id):
    user = get_object_or_404(UserInfo, pk=user_id)
    old_email = user.email  # Get the old email from the user instance

    if request.method == 'POST':
        form = UpdateUserInfoForm(request.POST, instance=user)  # Provide instance=user here
        if form.is_valid():
            new_email = form.cleaned_data['email']  # Get the new email from the form
            new_profile = form.cleaned_data['profile']  # Get the new user profile

            if new_email != old_email:
                # Email was changed, so check if the new email is unique
                if UserInfo.objects.exclude(id=user_id).filter(email=new_email).exists():
                    messages.error(request, "The new email is already in use.", extra_tags="danger")
                    return redirect('edit_user', user_id=user_id)

            user.profile = new_profile  # Set user profile
            form.save()  # Update the user instance with the new data
            messages.success(request, "User details updated successfully.")
            return redirect('manage_users')
    else:
        form = UpdateUserInfoForm(instance=user)
    return render(request, 'user_manager/edit_user.html', {'user': user, 'form': form, 'profiles': hotspot_profiles})


# Function to toggle enabling and disabling user account
# if toggled to enable the user is added to the list of users that will receive notification
# and their details populated in the radius database
@transaction.atomic
def toggle_enable_user(request, user_id):
    user = get_object_or_404(UserInfo, pk=user_id)

    if request.method == 'POST':
        if user.profile == '':
            messages.error(request, "You can only enable a user with a set profile. Edit the user's profile first.",
                           extra_tags="danger")
            return redirect('manage_users')

        if user.isenabled:
            # Disable the user
            user.isenabled = False
            user.save()
            messages.success(request, "User disabled successfully.")
        else:
            # Enable the user and generate a password if it's empty
            if not user.portalloginpassword:
                # Generate a random password
                user.portalloginpassword = generate_random_password(8)

            if not user.username:
                # Generate a unique username
                username = generate_username(user.firstname, user.lastname)
                # while the username exist generate a new one
                while UserInfo.objects.filter(username=username).exists():
                    username = generate_username(user.firstname, user.lastname)
                user.username = username
            user.isenabled = True
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
