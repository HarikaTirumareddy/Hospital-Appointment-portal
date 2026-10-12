import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from .models import Department, Doctor, PatientProfile, Appointment, MedicalReport

class HospitalPortalComprehensiveTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create department
        self.cardiology = Department.objects.create(
            name='Cardiology',
            slug='cardiology',
            description='Heart and cardiovascular health'
        )
        self.pediatrics = Department.objects.create(
            name='Pediatrics',
            slug='pediatrics',
            description='Child and infant healthcare'
        )
        self.orthopedics = Department.objects.create(
            name='Orthopedics',
            slug='orthopedics',
            description='Bone and joint health'
        )
        self.neurology = Department.objects.create(
            name='Neurology',
            slug='neurology',
            description='Brain and nervous system'
        )

        # Create doctor
        self.doctor = Doctor.objects.create(
            name='Dr. Test Vance, MD',
            department=self.cardiology,
            specialization='Cardiologist',
            qualifications='MBBS, MD',
            consultation_fee=500.00
        )

        # Create patients
        self.patient1 = User.objects.create_user(
            username='patient1',
            email='p1@example.com',
            password='password123',
            first_name='Alice',
            last_name='Smith'
        )
        PatientProfile.objects.create(user=self.patient1, phone='1234567890', blood_group='A+')

        self.patient2 = User.objects.create_user(
            username='patient2',
            email='p2@example.com',
            password='password123',
            first_name='Bob',
            last_name='Jones'
        )
        PatientProfile.objects.create(user=self.patient2, phone='9876543210', blood_group='O+')

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staffadmin',
            email='staff@hospital.com',
            password='adminpassword123',
            is_staff=True
        )

    def test_department_and_doctor_creation(self):
        """Verify 4 required departments and doctor associations exist"""
        self.assertEqual(Department.objects.count(), 4)
        self.assertTrue(Department.objects.filter(name='Cardiology').exists())
        self.assertTrue(Department.objects.filter(name='Pediatrics').exists())
        self.assertTrue(Department.objects.filter(name='Orthopedics').exists())
        self.assertTrue(Department.objects.filter(name='Neurology').exists())
        self.assertEqual(self.doctor.department.name, 'Cardiology')

    def test_double_booking_prevention_at_model_level(self):
        """Requirement #6: Prevent double booking for the same doctor, date, and time"""
        booking_date = timezone.now().date() + datetime.timedelta(days=2)
        slot = '10:00'

        # 1. Patient 1 books the slot
        apt1 = Appointment(
            patient=self.patient1,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot=slot,
            status=Appointment.STATUS_PENDING,
            symptoms_or_reason='Routine heart check'
        )
        apt1.full_clean()
        apt1.save()

        # 2. Patient 2 attempts to book the EXACT SAME doctor, date, and slot
        apt2 = Appointment(
            patient=self.patient2,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot=slot,
            status=Appointment.STATUS_PENDING,
            symptoms_or_reason='Chest pain'
        )
        
        # clean() method should raise ValidationError
        with self.assertRaises(ValidationError):
            apt2.full_clean()

        # Database UniqueConstraint should also reject duplicate saving
        with self.assertRaises(IntegrityError):
            apt2.save()

    def test_booking_allowed_after_cancellation(self):
        """If an appointment was Cancelled, the slot becomes bookable again"""
        booking_date = timezone.now().date() + datetime.timedelta(days=3)
        slot = '11:00'

        apt1 = Appointment.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot=slot,
            status=Appointment.STATUS_PENDING,
            symptoms_or_reason='Checkup'
        )

        # Cancel appointment 1
        apt1.status = Appointment.STATUS_CANCELLED
        apt1.save()

        # Patient 2 can now book this slot without conflicts
        apt2 = Appointment(
            patient=self.patient2,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot=slot,
            status=Appointment.STATUS_PENDING,
            symptoms_or_reason='Checkup'
        )
        apt2.full_clean()
        apt2.save()
        self.assertEqual(Appointment.objects.filter(doctor=self.doctor, appointment_date=booking_date, time_slot=slot).count(), 2)
        self.assertEqual(Appointment.objects.filter(doctor=self.doctor, appointment_date=booking_date, time_slot=slot, status='Pending').count(), 1)

    def test_api_booked_slots(self):
        """API endpoint should return active booked slots for dynamic JavaScript slot disabling"""
        booking_date = timezone.now().date() + datetime.timedelta(days=4)
        Appointment.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot='09:00',
            status=Appointment.STATUS_CONFIRMED,
            symptoms_or_reason='Consultation'
        )

        response = self.client.get(reverse('api_booked_slots'), {
            'doctor_id': self.doctor.id,
            'date': booking_date.strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('09:00', data['booked_slots'])

    def test_patient_dashboard_view(self):
        """Patient dashboard loads with upcoming, past, and report records"""
        self.client.login(username='patient1', password='password123')
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patient Dashboard')

    def test_staff_dashboard_access_control(self):
        """Non-staff users cannot access staff dashboard; staff users can"""
        # Regular patient
        self.client.login(username='patient1', password='password123')
        response = self.client.get(reverse('staff_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirects to login

        # Staff user
        self.client.login(username='staffadmin', password='adminpassword123')
        response = self.client.get(reverse('staff_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff & Doctor Operations Dashboard')

    def test_staff_can_update_status(self):
        """Staff can update appointment status (Pending -> Confirmed -> Completed)"""
        booking_date = timezone.now().date() + datetime.timedelta(days=1)
        apt = Appointment.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot='14:00',
            status=Appointment.STATUS_PENDING,
            symptoms_or_reason='Initial checkup'
        )

        self.client.login(username='staffadmin', password='adminpassword123')
        response = self.client.post(reverse('staff_update_status', args=[apt.id]), {
            'status': Appointment.STATUS_CONFIRMED
        })
        self.assertEqual(response.status_code, 302)

        apt.refresh_from_db()
        self.assertEqual(apt.status, Appointment.STATUS_CONFIRMED)

    def test_medical_report_linked_to_patient(self):
        """Medical reports are viewable by patient and staff"""
        report = MedicalReport.objects.create(
            title='Cardiac Stress Test Evaluation',
            patient=self.patient1,
            doctor=self.doctor,
            report_type='Consultation Summary',
            diagnosis='Normal sinus rhythm. Mild sinus tachycardia on exertion.',
            prescription_notes='Continue regular aerobic exercise and low sodium diet.'
        )

        self.client.login(username='patient1', password='password123')
        response = self.client.get(reverse('medical_report_detail', args=[report.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cardiac Stress Test Evaluation')
        self.assertContains(response, 'ApexCare Hospital')

    def test_patient_registration_flow(self):
        """Test full patient registration with user and medical profile"""
        response = self.client.post(reverse('patient_register'), {
            'username': 'newpatient',
            'first_name': 'Sarah',
            'last_name': 'Connor',
            'email': 'sarah@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'phone': '+15550001111',
            'gender': 'Female',
            'blood_group': 'B+',
            'date_of_birth': '1995-04-12',
            'address': 'Los Angeles, CA',
            'emergency_contact': '+15559990000'
        })
        self.assertEqual(response.status_code, 302)  # Redirects to login
        self.assertTrue(User.objects.filter(username='newpatient').exists())
        new_user = User.objects.get(username='newpatient')
        self.assertEqual(new_user.patient_profile.phone, '+15550001111')
        self.assertEqual(new_user.patient_profile.blood_group, 'B+')

    def test_patient_login_and_logout(self):
        """Test patient login and logout views"""
        # Login
        response = self.client.post(reverse('patient_login'), {
            'username': 'patient1',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

        # Logout
        response = self.client.get(reverse('patient_logout'))
        self.assertEqual(response.status_code, 302)

    def test_appointment_booking_server_validation_rejects_duplicate(self):
        """Form submission rejects duplicate booking for the same doctor, date, and slot"""
        self.client.login(username='patient1', password='password123')
        booking_date = (timezone.now().date() + datetime.timedelta(days=5)).strftime('%Y-%m-%d')
        slot = '15:00'

        # 1. First booking succeeds
        response1 = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': booking_date,
            'time_slot': slot,
            'symptoms_or_reason': 'First booking reason'
        })
        self.assertEqual(response1.status_code, 302)
        self.assertTrue(Appointment.objects.filter(doctor=self.doctor, appointment_date=booking_date, time_slot=slot).exists())

        # 2. Patient 2 logs in and tries to book identical doctor, date, and slot
        self.client.login(username='patient2', password='password123')
        response2 = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': booking_date,
            'time_slot': slot,
            'symptoms_or_reason': 'Second conflicting booking'
        })
        # Form should be invalid and re-rendered with error status
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'already has a confirmed or pending booking at this time')
