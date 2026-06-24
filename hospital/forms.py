from datetime import date
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Appointment, OnlineConsultation, Prescription, Testimonial

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=80, required=False)
    last_name = forms.CharField(max_length=80, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user


class EmailLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user_obj = User.objects.filter(email__iexact=email).first()
            username = user_obj.username if user_obj else email
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Invalid email or password.')
            cleaned_data['user'] = user
        return cleaned_data


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['name', 'email', 'phone', 'appointment_date', 'appointment_time', 'symptoms']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'symptoms': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe symptoms or reason for visit'}),
        }

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data['appointment_date']
        if appointment_date < date.today():
            raise forms.ValidationError('Appointment date cannot be in the past.')
        return appointment_date


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = OnlineConsultation
        fields = ['doctor', 'problem_title', 'description', 'preferred_date']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [
            'doctor', 'title', 'patient_name', 'patient_age', 'patient_gender',
            'diagnosis', 'medicines', 'instructions', 'follow_up_date', 'file', 'note'
        ]
        widgets = {
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Diagnosis or condition'}),
            'medicines': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Example: Paracetamol 500mg - 1 tablet - 3 times daily - 3 days'}),
            'instructions': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Advice, precautions, rest, diet, review instructions'}),
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Extra note'}),
        }


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['patient_name', 'patient_role', 'rating', 'message', 'patient_image']
        labels = {
            'patient_name': 'Your name',
            'patient_role': 'Treatment / patient type',
            'patient_image': 'Your photo (optional)',
        }
        widgets = {
            'patient_name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'patient_role': forms.TextInput(attrs={'placeholder': 'Example: Surgery Patient'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Share your experience with our hospital'}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating') or 5
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating
