from datetime import timezone
from django import forms
from .models import Todo
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from captcha.fields import CaptchaField
import re
from captcha.fields import CaptchaField


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

        error_messages = {
            'title': {
                'required': 'Title is required. Please provide a title for the task.',
                'max_length': 'Title is too long. It must be under 100 characters.',
            },
            'description': {
                'required': 'Description is required. Please provide a description.',
            },
            'start_date': {
                'required': 'Start date is required. Please select a start date.',
                'invalid': 'Enter a valid date for the start date.',
            },
            'end_date': {
                'required': 'End date is required. Please select an end date.',
                'invalid': 'Enter a valid date for the end date.',
                'invalid_date': 'End date cannot be earlier than start date.',
            },
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date: 
            if end_date < start_date:
                raise ValidationError("End date cannot be earlier than start date.")
        return cleaned_data
    

class SignupForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
        required=True,  # Make the field required
        error_messages={'required': 'First name is required'} 
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
        required=True,  # Make the field required
        error_messages={'required': 'Last name is required'}  
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
        required=True,  # Make the field required
        error_messages={'required': 'Email is required'}  
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}),
        required=True,  # Make the field required
        error_messages={'required': 'Password is required'}  
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}),
        required=True,  # Make the field required
        error_messages={'required': 'Confirm password is required'} 
    )
    captcha = CaptchaField(
        required=True,  # Make the captcha field required
        error_messages={'required': 'Please solve the captcha.'}  
    )

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name.isalpha():
            raise forms.ValidationError("First name should only contain letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name.isalpha():
            raise forms.ValidationError("Last name should only contain letters.")
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@gmail.com"):
            raise forms.ValidationError("Only Gmail accounts are allowed.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one number.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        required=True, 
        error_messages={'required': 'Email is required'}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        required=True,
        error_messages={'required': 'Password is required'}
    )
    