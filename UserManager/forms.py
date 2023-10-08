from django import forms

from .models import Registration


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['first_name', 'last_name', 'email', 'telephone_number', 'terms_and_conditions']

    def clean(self):
        cleaned_data = super().clean()
        # Check if a user with the same email already exists
        email = cleaned_data.get('email')
        if email and Registration.objects.filter(email=email).exists():
            self.add_error('email', "A user with this email already exists.")

            telephone_number = cleaned_data.get('telephone_number')
            # Check validate telephone number already in database first
            if telephone_number and Registration.objects.filter(telephone_number=telephone_number).exists():
                self.add_error('telephone_number', "A user with this telephone number already exists.")

        return cleaned_data


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['first_name', 'last_name', 'email', 'telephone_number', 'profile']
