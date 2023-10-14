from django import forms

from .models import UserInfo


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['firstname', 'lastname', 'email', 'mobilephone', 'termsandconditions']

    def clean(self):
        cleaned_data = super().clean()
        # Check if a user with the same email already exists
        email = cleaned_data.get('email')
        if email and UserInfo.objects.filter(email=email).exists():
            self.add_error('email', "A user with this email already exists.")

            mp = cleaned_data.get('mobilephone')
            # Check validate telephone number already in database first
            if mp and UserInfo.objects.filter(mobilephone=mp).exists():
                self.add_error('mobilephone', "A user with this mobile number already exists.")

        return cleaned_data


class UpdateUserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['firstname', 'lastname', 'email', 'mobilephone', 'profile']
