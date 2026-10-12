from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Department, Doctor, PatientProfile, Appointment, MedicalReport, Patient

class PatientRegistrationForm(forms.ModelForm):
    """User Registration Form with Patient Profile fields"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unique username'})
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'patient@example.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )
    
    # Profile fields
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices=PatientProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    blood_group = forms.ChoiceField(
        choices=[('', 'Select Blood Group (Optional)')] + PatientProfile.BLOOD_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Residential address'})
    )
    emergency_contact = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency contact phone'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender=self.cleaned_data.get('gender', 'Male'),
                blood_group=self.cleaned_data.get('blood_group', ''),
                address=self.cleaned_data.get('address', ''),
                emergency_contact=self.cleaned_data.get('emergency_contact', '')
            )
        return user


class PatientProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    gender = forms.ChoiceField(choices=PatientProfile.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    blood_group = forms.ChoiceField(
        choices=[('', 'Select Blood Group')] + PatientProfile.BLOOD_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    emergency_contact = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = PatientProfile
        fields = ['phone', 'date_of_birth', 'gender', 'blood_group', 'address', 'emergency_contact']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        return profile


class AppointmentBookingForm(forms.ModelForm):
    """Appointment Booking Form with real-time validation against double bookings"""
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_available=True).select_related('department'),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor'}),
        empty_label="-- Select Doctor --"
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control', 
            'type': 'date', 
            'id': 'id_appointment_date'
        })
    )
    time_slot = forms.ChoiceField(
        choices=[('', '-- Select Time Slot --')] + Appointment.TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_time_slot'})
    )
    symptoms_or_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Describe your symptoms or reason for visit (e.g., severe migraine, routine checkup, chest pain...)'
        })
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'time_slot', 'symptoms_or_reason']

    def clean_appointment_date(self):
        selected_date = self.cleaned_data.get('appointment_date')
        if selected_date and selected_date < timezone.now().date():
            raise ValidationError("You cannot book an appointment for a date in the past.")
        return selected_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('time_slot')

        if doctor and appointment_date and time_slot:
            # Check for double booking
            existing = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                time_slot=time_slot
            ).exclude(status=Appointment.STATUS_CANCELLED)

            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError(
                    f"Dr. {doctor.name} already has a confirmed or pending booking at this time ({time_slot}). Please choose a different slot or another date."
                )

        return cleaned_data


class AppointmentStatusUpdateForm(forms.ModelForm):
    """Staff form to update appointment status"""
    status = forms.ChoiceField(
        choices=Appointment.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cancellation_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Reason for cancellation (optional)'})
    )

    class Meta:
        model = Appointment
        fields = ['status', 'cancellation_reason']


class DoctorForm(forms.ModelForm):
    """Staff/Admin form to create or edit doctors"""
    class Meta:
        model = Doctor
        fields = [
            'name', 'department', 'specialization', 'qualifications', 
            'experience_years', 'email', 'phone', 'consultation_fee', 
            'room_number', 'available_days', 'bio', 'image', 'is_available'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dr. John Doe'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Interventional Cardiologist'}),
            'qualifications': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MBBS, MD, DM'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Room 204, 2nd Floor'}),
            'available_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Monday - Friday, 9am - 5pm'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MedicalReportForm(forms.ModelForm):
    """Form to create or upload a Medical Report"""
    class Meta:
        model = MedicalReport
        fields = ['title', 'patient', 'doctor', 'appointment', 'report_type', 'diagnosis', 'prescription_notes', 'report_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Echocardiogram Report / General Consultation'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clinical diagnosis and findings...'}),
            'prescription_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Prescription and doctor advice...'}),
            'report_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sort patient dropdown nicely
        self.fields['patient'].queryset = User.objects.filter(patient_profile__isnull=False).order_by('first_name', 'username')
        self.fields['appointment'].required = False
        self.fields['doctor'].required = False
