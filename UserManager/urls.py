"""
URL configuration for UserManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from UserManager import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_to_mikrotik, name='login'),
    path('registration/', views.registration, name='registration'),
    path('registration/success/', views.registration_success, name='registration_success'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('toggle_enable_user/<int:user_id>/', views.toggle_enable_user, name='toggle_enable_user'),

]
