from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Department(models.Model):
    """Hospital department (e.g. Cardiology, Pediatrics, Orthopedics, Neurology)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(
        max_length=50, 
        default='bi-heart-pulse',
        help_text="Bootstrap icon class, e.g. bi-heart-pulse, bi-balloon, bi-activity, bi-bandaid"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Doctor(models.Model):
    """Doctor details, department affiliation, consultation fee and availability"""
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='doctor_profile',
        help_text="Optional login account for this doctor"
    )
    name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    specialization = models.CharField(max_length=200)
    qualifications = models.CharField(max_length=200, help_text="e.g. MBBS, MD, MS, FRCS")
    experience_years = models.PositiveIntegerField(default=5)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=500.00)
    room_number = models.CharField(max_length=50, default="Room 101")
    available_days = models.CharField(max_length=150, default="Monday - Friday")
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class PatientProfile(models.Model):
    """Extended patient information linked to Django User"""
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.phone}"


# Model Alias for Patient
Patient = PatientProfile


class Appointment(models.Model):
    """Patient appointment with doctor, date, time slot, and status"""
    STATUS_PENDING = 'Pending'
    STATUS_CONFIRMED = 'Confirmed'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    TIME_SLOT_CHOICES = [
        ('09:00', '09:00 AM - 09:30 AM'),
        ('09:30', '09:30 AM - 10:00 AM'),
        ('10:00', '10:00 AM - 10:30 AM'),
        ('10:30', '10:30 AM - 11:00 AM'),
        ('11:00', '11:00 AM - 11:30 AM'),
        ('11:30', '11:30 AM - 12:00 PM'),
        ('14:00', '02:00 PM - 02:30 PM'),
        ('14:30', '02:30 PM - 03:00 PM'),
        ('15:00', '03:00 PM - 03:30 PM'),
        ('15:30', '03:30 PM - 04:00 PM'),
        ('16:00', '04:00 PM - 04:30 PM'),
        ('16:30', '04:30 PM - 05:00 PM'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    symptoms_or_reason = models.TextField(help_text="Primary reason for booking or symptoms")
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', 'time_slot']
        constraints = [
            # Prevent double booking for the same doctor, date, and time slot unless previous booking was Cancelled
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'time_slot'],
                condition=~models.Q(status='Cancelled'),
                name='unique_active_doctor_appointment_slot'
            )
        ]

    def clean(self):
        super().clean()
        # Prevent booking in the past
        if self.appointment_date and self.appointment_date < timezone.now().date():
            raise ValidationError({'appointment_date': "Appointment date cannot be in the past."})

        # Check for slot double booking
        if self.doctor and self.appointment_date and self.time_slot and self.status != self.STATUS_CANCELLED:
            conflicting = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                time_slot=self.time_slot
            ).exclude(status=self.STATUS_CANCELLED)

            if self.pk:
                conflicting = conflicting.exclude(pk=self.pk)

            if conflicting.exists():
                raise ValidationError(
                    f"Dr. {self.doctor.name} already has an active appointment for {self.appointment_date} at {self.get_time_slot_display()}. Please select another slot."
                )

    def __str__(self):
        return f"{self.patient.username} with {self.doctor.name} on {self.appointment_date} at {self.time_slot} ({self.status})"


class MedicalReport(models.Model):
    """Medical reports linked to patients and optionally specific appointments"""
    REPORT_TYPE_CHOICES = [
        ('Consultation Summary', 'Consultation Summary'),
        ('Laboratory Test', 'Laboratory Test'),
        ('Prescription', 'Prescription'),
        ('Imaging / X-Ray', 'Imaging / X-Ray'),
        ('Discharge Summary', 'Discharge Summary'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_reports')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES, default='Consultation Summary')
    diagnosis = models.TextField(blank=True, help_text="Clinical diagnosis / clinical findings")
    prescription_notes = models.TextField(blank=True, help_text="Medications prescribed or instructions")
    report_file = models.FileField(upload_to='medical_reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name() or self.patient.username}"
