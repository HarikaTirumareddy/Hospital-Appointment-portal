import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from portal.models import Department, Doctor, PatientProfile, Appointment, MedicalReport

class Command(BaseCommand):
    help = "Seed database with departments, doctors, demo admin, and sample patient with appointments."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Hospital Portal database..."))

        # 1. Departments
        departments_data = [
            {
                'name': 'Cardiology',
                'slug': 'cardiology',
                'description': 'Advanced cardiovascular diagnosis, heart failure management, ECG, echocardiography, and interventional cardiology.',
                'icon_class': 'bi-heart-pulse-fill'
            },
            {
                'name': 'Pediatrics',
                'slug': 'pediatrics',
                'description': 'Compassionate child health, neonatal care, growth monitoring, immunizations, and pediatric emergency services.',
                'icon_class': 'bi-balloon-heart-fill'
            },
            {
                'name': 'Orthopedics',
                'slug': 'orthopedics',
                'description': 'Comprehensive bone, joint, spine, sports medicine, trauma rehabilitation, and minimally invasive joint replacement.',
                'icon_class': 'bi-person-walking'
            },
            {
                'name': 'Neurology',
                'slug': 'neurology',
                'description': 'Specialized brain and nervous system care, stroke management, epilepsy, migraines, and neuromuscular disorders.',
                'icon_class': 'bi-activity'
            },
            {
                'name': 'General Medicine',
                'slug': 'general-medicine',
                'description': 'Holistic primary care, chronic condition management (hypertension, diabetes), routine health checkups, and wellness.',
                'icon_class': 'bi-hospital'
            },
            {
                'name': 'Dermatology',
                'slug': 'dermatology',
                'description': 'Clinical dermatology, skin disease therapies, allergy management, laser procedures, and cosmetic skin wellness.',
                'icon_class': 'bi-shield-plus'
            },
        ]

        departments_map = {}
        for dep in departments_data:
            obj, created = Department.objects.get_or_create(
                slug=dep['slug'],
                defaults=dep
            )
            departments_map[dep['slug']] = obj
            if created:
                self.stdout.write(f"  + Department created: {obj.name}")

        # 2. Doctors
        doctors_data = [
            {
                'name': 'Dr. Robert Vance, MD',
                'department': departments_map['cardiology'],
                'specialization': 'Senior Interventional Cardiologist',
                'qualifications': 'MBBS, MD (Medicine), DM (Cardiology), FACC',
                'experience_years': 14,
                'email': 'dr.robert.vance@hospital.com',
                'phone': '+1 (555) 234-5678',
                'consultation_fee': 750.00,
                'room_number': 'Suite 201, Heart Wing',
                'available_days': 'Monday to Friday',
                'bio': 'Dr. Vance has over 14 years of clinical experience specializing in angioplasty, heart failure therapies, and preventive cardiology.'
            },
            {
                'name': 'Dr. Elena Rostova, MD',
                'department': departments_map['cardiology'],
                'specialization': 'Clinical & Pediatric Cardiologist',
                'qualifications': 'MBBS, MD (Cardiology), FESC',
                'experience_years': 9,
                'email': 'dr.elena.rostova@hospital.com',
                'phone': '+1 (555) 234-5679',
                'consultation_fee': 600.00,
                'room_number': 'Suite 203, Heart Wing',
                'available_days': 'Tuesday, Thursday, Saturday',
                'bio': 'Specialized in non-invasive cardiac imaging, congenital heart disorders, and complex arrhythmias.'
            },
            {
                'name': 'Dr. Marcus Sterling, MD',
                'department': departments_map['pediatrics'],
                'specialization': 'Chief of Pediatric Medicine & Neonatology',
                'qualifications': 'MBBS, MD (Pediatrics), FAAP',
                'experience_years': 12,
                'email': 'dr.marcus.sterling@hospital.com',
                'phone': '+1 (555) 345-6780',
                'consultation_fee': 500.00,
                'room_number': 'Room 105, Children Clinic',
                'available_days': 'Monday to Saturday',
                'bio': 'Known for warm bedside manner, Dr. Sterling handles infant developmental assessments, childhood allergies, and acute pediatric care.'
            },
            {
                'name': 'Dr. Priya Sharma, MD',
                'department': departments_map['pediatrics'],
                'specialization': 'Pediatric Pulmonology & Critical Care',
                'qualifications': 'MBBS, DCH, MD (Pediatrics)',
                'experience_years': 8,
                'email': 'dr.priya.sharma@hospital.com',
                'phone': '+1 (555) 345-6781',
                'consultation_fee': 450.00,
                'room_number': 'Room 108, Children Clinic',
                'available_days': 'Monday, Wednesday, Friday',
                'bio': 'Passionate about respiratory disorders in young children, asthma therapies, and childhood immunization programs.'
            },
            {
                'name': 'Dr. James Thorne, MS',
                'department': departments_map['orthopedics'],
                'specialization': 'Joint Replacement & Spine Surgeon',
                'qualifications': 'MBBS, MS (Orthopedics), M.Ch (Ortho)',
                'experience_years': 16,
                'email': 'dr.james.thorne@hospital.com',
                'phone': '+1 (555) 456-7890',
                'consultation_fee': 800.00,
                'room_number': 'Room 304, Ortho Center',
                'available_days': 'Monday, Tuesday, Thursday',
                'bio': 'Dr. Thorne has performed more than 2,000 successful hip and knee arthroplasties with cutting-edge robotic guidance.'
            },
            {
                'name': 'Dr. Sophia Morales, MS',
                'department': departments_map['orthopedics'],
                'specialization': 'Sports Medicine & Arthroscopy Specialist',
                'qualifications': 'MBBS, MS (Orthopedics), Fellowship Sports Med',
                'experience_years': 7,
                'email': 'dr.sophia.morales@hospital.com',
                'phone': '+1 (555) 456-7891',
                'consultation_fee': 550.00,
                'room_number': 'Room 306, Ortho Center',
                'available_days': 'Wednesday, Friday, Saturday',
                'bio': 'Focuses on ACL reconstructions, shoulder rotator cuff repairs, and non-surgical athletic rehabilitation.'
            },
            {
                'name': 'Dr. Alan Turing-Hayes, DM',
                'department': departments_map['neurology'],
                'specialization': 'Senior Neurologist & Stroke Care Lead',
                'qualifications': 'MBBS, MD (Medicine), DM (Neurology)',
                'experience_years': 15,
                'email': 'dr.alan.turing@hospital.com',
                'phone': '+1 (555) 567-8901',
                'consultation_fee': 850.00,
                'room_number': 'Room 402, Neuro Wing',
                'available_days': 'Monday to Friday',
                'bio': 'Pioneer in comprehensive neurovascular interventions, acute stroke management, and epilepsy diagnosis.'
            },
            {
                'name': 'Dr. Claire Chen, DM',
                'department': departments_map['neurology'],
                'specialization': 'Cognitive Neurology & Headache Specialist',
                'qualifications': 'MBBS, MD, DM (Neurology), FAAN',
                'experience_years': 10,
                'email': 'dr.claire.chen@hospital.com',
                'phone': '+1 (555) 567-8902',
                'consultation_fee': 700.00,
                'room_number': 'Room 405, Neuro Wing',
                'available_days': 'Tuesday, Thursday, Saturday',
                'bio': 'Dedicated to early diagnosis of memory disorders, Parkinson disease management, and refractory migraine care.'
            },
            {
                'name': 'Dr. Arthur Pendelton, MD',
                'department': departments_map['general-medicine'],
                'specialization': 'Internal Medicine & Geriatric Specialist',
                'qualifications': 'MBBS, MD (Internal Medicine)',
                'experience_years': 18,
                'email': 'dr.arthur.p@hospital.com',
                'phone': '+1 (555) 678-9012',
                'consultation_fee': 400.00,
                'room_number': 'Room 101, Main OPD',
                'available_days': 'Monday to Saturday',
                'bio': 'Comprehensive family health care, annual wellness screenings, and chronic illness coordination.'
            },
            {
                'name': 'Dr. Zoe Martinez, MD',
                'department': departments_map['dermatology'],
                'specialization': 'Consultant Dermatologist & Dermatosurgeon',
                'qualifications': 'MBBS, MD (Dermatology, Venereology & Leprosy)',
                'experience_years': 8,
                'email': 'dr.zoe.martinez@hospital.com',
                'phone': '+1 (555) 789-0123',
                'consultation_fee': 500.00,
                'room_number': 'Room 215, Specialty Clinic',
                'available_days': 'Monday to Friday',
                'bio': 'Expertise in eczema, psoriasis, acne management, skin cancer screenings, and aesthetic therapies.'
            },
        ]

        doctors_map = {}
        for doc in doctors_data:
            obj, created = Doctor.objects.get_or_create(
                email=doc['email'],
                defaults=doc
            )
            doctors_map[doc['name']] = obj
            if created:
                self.stdout.write(f"  + Doctor created: {obj.name}")

        # 3. Superuser / Admin
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@hospital.com',
                'first_name': 'Hospital',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if admin_created:
            admin_user.set_password('adminpassword123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("  + Created Superuser/Staff: admin (password: adminpassword123)"))
        else:
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password('adminpassword123')
            admin_user.save()

        # 4. Demo Patient
        patient_user, patient_created = User.objects.get_or_create(
            username='john_patient',
            defaults={
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        if patient_created:
            patient_user.set_password('patientpassword123')
            patient_user.save()
            self.stdout.write(self.style.SUCCESS("  + Created Demo Patient: john_patient (password: patientpassword123)"))
        else:
            patient_user.set_password('patientpassword123')
            patient_user.save()

        profile, prof_created = PatientProfile.objects.get_or_create(
            user=patient_user,
            defaults={
                'phone': '+1 (555) 987-6543',
                'date_of_birth': datetime.date(1992, 5, 14),
                'gender': 'Male',
                'blood_group': 'O+',
                'address': '742 Evergreen Terrace, Springfield',
                'emergency_contact': '+1 (555) 999-1122 (Wife: Jane Doe)'
            }
        )

        # 5. Sample Appointments for Demo Patient
        today = timezone.now().date()
        doc_vance = doctors_map.get('Dr. Robert Vance, MD')
        doc_sterling = doctors_map.get('Dr. Marcus Sterling, MD')
        doc_thorne = doctors_map.get('Dr. James Thorne, MS')
        doc_alan = doctors_map.get('Dr. Alan Turing-Hayes, DM')

        # Upcoming appointment 1
        if doc_vance:
            apt1, _ = Appointment.objects.get_or_create(
                patient=patient_user,
                doctor=doc_vance,
                appointment_date=today + datetime.timedelta(days=2),
                time_slot='10:00',
                defaults={
                    'status': Appointment.STATUS_CONFIRMED,
                    'symptoms_or_reason': 'Follow-up consultation for mild chest discomfort during exertion and ECG review.'
                }
            )

        # Upcoming appointment 2
        if doc_thorne:
            apt2, _ = Appointment.objects.get_or_create(
                patient=patient_user,
                doctor=doc_thorne,
                appointment_date=today + datetime.timedelta(days=5),
                time_slot='14:00',
                defaults={
                    'status': Appointment.STATUS_PENDING,
                    'symptoms_or_reason': 'Persistent right knee ache following morning jog.'
                }
            )

        # Past completed appointment
        past_apt = None
        if doc_alan:
            past_apt, _ = Appointment.objects.get_or_create(
                patient=patient_user,
                doctor=doc_alan,
                appointment_date=today - datetime.timedelta(days=10),
                time_slot='11:00',
                defaults={
                    'status': Appointment.STATUS_COMPLETED,
                    'symptoms_or_reason': 'Recurrent tension headaches and light sensitivity.'
                }
            )

        # 6. Sample Medical Report for the completed appointment
        if past_apt and doc_alan:
            MedicalReport.objects.get_or_create(
                patient=patient_user,
                title='Neurological Evaluation & Headache Diagnosis',
                defaults={
                    'doctor': doc_alan,
                    'appointment': past_apt,
                    'report_type': 'Consultation Summary',
                    'diagnosis': 'Frequent episodic tension-type headache triggered by prolonged screen time and mild cervical posture strain. Cranial nerve examination normal. Reflexes intact.',
                    'prescription_notes': '1. Tab. Naproxen 500mg as needed for severe episode (max 2/day).\n2. Ergonomic workstation adjustments; 20-20-20 screen rule.\n3. Adequate hydration (min 2.5L/day).\n4. Follow up after 4 weeks if frequency exceeds 2 episodes weekly.'
                }
            )
            self.stdout.write("  + Created Sample Medical Report for John Doe")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with all required departments, doctors, accounts, and appointments!"))
