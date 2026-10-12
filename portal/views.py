from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.models import User

from .models import Department, Doctor, PatientProfile, Appointment, MedicalReport, Patient
from .forms import (
    PatientRegistrationForm, 
    PatientProfileUpdateForm,
    AppointmentBookingForm, 
    AppointmentStatusUpdateForm,
    DoctorForm,
    MedicalReportForm
)

def is_staff_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# --- 1. HOME VIEW ---
def home_view(request):
    departments = Department.objects.filter(is_active=True).annotate(doc_count=Count('doctors'))
    featured_doctors = Doctor.objects.filter(is_available=True).select_related('department')[:6]
    
    # Hospital metrics for showcase
    total_doctors = Doctor.objects.filter(is_available=True).count()
    total_departments = departments.count()
    completed_appointments = Appointment.objects.filter(status=Appointment.STATUS_COMPLETED).count()
    total_patients = PatientProfile.objects.count()

    context = {
        'departments': departments,
        'featured_doctors': featured_doctors,
        'stats': {
            'doctors': total_doctors,
            'departments': total_departments,
            'completed_appointments': completed_appointments,
            'patients': total_patients,
        }
    }
    return render(request, 'portal/home.html', context)


# --- 2. DOCTOR DIRECTORY & JAVASCRIPT FILTERING ---
def doctor_list_view(request):
    departments = Department.objects.filter(is_active=True)
    doctors = Doctor.objects.filter(is_available=True).select_related('department')
    
    context = {
        'departments': departments,
        'doctors': doctors,
    }
    return render(request, 'portal/doctor_list.html', context)


def doctor_detail_view(request, pk):
    doctor = get_object_or_404(Doctor.objects.select_related('department'), pk=pk)
    upcoming_slots_count = Appointment.objects.filter(
        doctor=doctor, 
        appointment_date=timezone.now().date()
    ).exclude(status=Appointment.STATUS_CANCELLED).count()

    context = {
        'doctor': doctor,
        'today_booked_count': upcoming_slots_count,
        'total_slots': len(Appointment.TIME_SLOT_CHOICES),
    }
    return render(request, 'portal/doctor_detail.html', context)


# --- 3. PATIENT AUTHENTICATION ---
def patient_register_view(request):
    if request.user.is_authenticated:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Welcome {user.first_name or user.username}! Your patient account has been created. Please log in.")
            return redirect('patient_login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PatientRegistrationForm()

    return render(request, 'portal/register.html', {'form': form})


def patient_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('staff_dashboard')
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_staff:
                return redirect('staff_dashboard')
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'portal/login.html', {'form': form})


@login_required
def patient_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


# --- 4. PATIENT DASHBOARD & PROFILE ---
@login_required
def patient_dashboard_view(request):
    today = timezone.now().date()
    
    # Upcoming appointments (today onwards, not cancelled or completed)
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        appointment_date__gte=today
    ).exclude(status__in=[Appointment.STATUS_CANCELLED, Appointment.STATUS_COMPLETED]).select_related('doctor', 'doctor__department').order_by('appointment_date', 'time_slot')

    # Past or concluded appointments
    past_appointments = Appointment.objects.filter(
        patient=request.user
    ).filter(
        Q(appointment_date__lt=today) | Q(status__in=[Appointment.STATUS_CANCELLED, Appointment.STATUS_COMPLETED])
    ).select_related('doctor', 'doctor__department').order_by('-appointment_date', 'time_slot')

    # Medical reports
    reports = MedicalReport.objects.filter(patient=request.user).select_related('doctor', 'appointment').order_by('-created_at')

    # Patient profile
    profile = getattr(request.user, 'patient_profile', None)

    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'reports': reports,
        'profile': profile,
        'today': today,
    }
    return render(request, 'portal/patient_dashboard.html', context)


@login_required
def patient_profile_edit_view(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PatientProfileUpdateForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = PatientProfileUpdateForm(instance=profile, user=request.user)

    return render(request, 'portal/profile_edit.html', {'form': form})


# --- 5. APPOINTMENT BOOKING & CANCELLATION ---
@login_required
def book_appointment_view(request):
    initial_data = {}
    selected_doctor_id = request.GET.get('doctor_id')
    if selected_doctor_id:
        initial_data['doctor'] = selected_doctor_id

    # Default to today's date
    today_str = timezone.now().date().strftime('%Y-%m-%d')
    initial_data['appointment_date'] = today_str

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = Appointment.STATUS_PENDING
            appointment.save()
            messages.success(
                request, 
                f"Appointment booked successfully with Dr. {appointment.doctor.name} on {appointment.appointment_date} at {appointment.get_time_slot_display()}! Status: Pending confirmation."
            )
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Could not book appointment. Please review the highlighted errors below.")
    else:
        form = AppointmentBookingForm(initial=initial_data)

    doctors = Doctor.objects.filter(is_available=True).select_related('department')
    time_slots = Appointment.TIME_SLOT_CHOICES

    context = {
        'form': form,
        'doctors': doctors,
        'time_slots': time_slots,
        'today_str': today_str,
    }
    return render(request, 'portal/book_appointment.html', context)


@login_required
def cancel_appointment_view(request, pk):
    # Only owner of appointment or staff can cancel
    if request.user.is_staff:
        appointment = get_object_or_404(Appointment, pk=pk)
    else:
        appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

    if appointment.status in [Appointment.STATUS_COMPLETED, Appointment.STATUS_CANCELLED]:
        messages.warning(request, f"This appointment is already {appointment.status.lower()} and cannot be cancelled.")
        return redirect('patient_dashboard')

    if request.method == 'POST':
        reason = request.POST.get('cancellation_reason', 'Cancelled by patient')
        appointment.status = Appointment.STATUS_CANCELLED
        appointment.cancellation_reason = reason
        appointment.save()
        messages.success(request, f"Appointment on {appointment.appointment_date} has been cancelled successfully.")
        
        if request.user.is_staff:
            return redirect('staff_dashboard')
        return redirect('patient_dashboard')

    return render(request, 'portal/cancel_appointment_confirm.html', {'appointment': appointment})


# --- 6. REAL-TIME API FOR BOOKED SLOTS (DOUBLE BOOKING PREVENTION) ---
def api_booked_slots(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({'booked_slots': []})

    try:
        booked = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date_str
        ).exclude(status=Appointment.STATUS_CANCELLED).values_list('time_slot', flat=True)

        return JsonResponse({'booked_slots': list(booked)})
    except Exception as e:
        return JsonResponse({'error': str(e), 'booked_slots': []}, status=400)


# --- 7. MEDICAL REPORTS VIEW ---
@login_required
def medical_report_detail_view(request, pk):
    if request.user.is_staff:
        report = get_object_or_404(MedicalReport.objects.select_related('patient', 'doctor', 'appointment'), pk=pk)
    else:
        report = get_object_or_404(MedicalReport.objects.select_related('patient', 'doctor', 'appointment'), pk=pk, patient=request.user)

    return render(request, 'portal/report_detail.html', {'report': report})


# --- 8. STAFF / ADMIN MANAGEMENT PORTAL ---
@user_passes_test(is_staff_check, login_url='patient_login')
def staff_dashboard_view(request):
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    date_filter = request.GET.get('date', '')

    appointments = Appointment.objects.select_related('patient', 'doctor', 'doctor__department').order_by('-appointment_date', 'time_slot')

    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(patient__username__icontains=search_query) |
            Q(doctor__name__icontains=search_query) |
            Q(doctor__department__name__icontains=search_query)
        )

    # Stats
    total_appointments = Appointment.objects.count()
    pending_count = Appointment.objects.filter(status=Appointment.STATUS_PENDING).count()
    confirmed_count = Appointment.objects.filter(status=Appointment.STATUS_CONFIRMED).count()
    completed_count = Appointment.objects.filter(status=Appointment.STATUS_COMPLETED).count()
    cancelled_count = Appointment.objects.filter(status=Appointment.STATUS_CANCELLED).count()
    total_doctors = Doctor.objects.count()

    context = {
        'appointments': appointments[:100],  # show recent 100
        'status_filter': status_filter,
        'search_query': search_query,
        'date_filter': date_filter,
        'statuses': [Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED, Appointment.STATUS_COMPLETED, Appointment.STATUS_CANCELLED],
        'stats': {
            'total': total_appointments,
            'pending': pending_count,
            'confirmed': confirmed_count,
            'completed': completed_count,
            'cancelled': cancelled_count,
            'doctors': total_doctors,
        }
    }
    return render(request, 'portal/staff_dashboard.html', context)


@user_passes_test(is_staff_check, login_url='patient_login')
def staff_update_status_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        reason = request.POST.get('cancellation_reason', '')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            if new_status == Appointment.STATUS_CANCELLED and reason:
                appointment.cancellation_reason = reason
            appointment.save()
            messages.success(request, f"Appointment #{appointment.id} status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status choice.")
    
    return redirect('staff_dashboard')


@user_passes_test(is_staff_check, login_url='patient_login')
def staff_doctors_view(request):
    doctors = Doctor.objects.select_related('department').order_by('department__name', 'name')
    return render(request, 'portal/staff_doctors.html', {'doctors': doctors})


@user_passes_test(is_staff_check, login_url='patient_login')
def staff_doctor_create_view(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Doctor Dr. {doctor.name} added successfully!")
            return redirect('staff_doctors')
        else:
            messages.error(request, "Please fix the errors in the doctor form.")
    else:
        form = DoctorForm()
    return render(request, 'portal/staff_doctor_form.html', {'form': form, 'title': 'Add New Doctor'})


@user_passes_test(is_staff_check, login_url='patient_login')
def staff_doctor_edit_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Doctor Dr. {doctor.name} updated successfully!")
            return redirect('staff_doctors')
        else:
            messages.error(request, "Please fix the errors in the doctor form.")
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'portal/staff_doctor_form.html', {'form': form, 'title': f'Edit Doctor: {doctor.name}'})


@user_passes_test(is_staff_check, login_url='patient_login')
def staff_doctor_delete_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        name = doctor.name
        doctor.delete()
        messages.success(request, f"Doctor Dr. {name} has been removed.")
        return redirect('staff_doctors')
    return render(request, 'portal/staff_doctor_delete_confirm.html', {'doctor': doctor})


@user_passes_test(is_staff_check, login_url='patient_login')
def staff_report_create_view(request):
    initial = {}
    appointment_id = request.GET.get('appointment_id')
    patient_id = request.GET.get('patient_id')
    if appointment_id:
        try:
            apt = Appointment.objects.get(pk=appointment_id)
            initial['appointment'] = apt
            initial['patient'] = apt.patient
            initial['doctor'] = apt.doctor
        except Appointment.DoesNotExist:
            pass
    elif patient_id:
        try:
            initial['patient'] = User.objects.get(pk=patient_id)
        except User.DoesNotExist:
            pass

    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save()
            messages.success(request, f"Medical report '{report.title}' created successfully for {report.patient.get_full_name() or report.patient.username}!")
            return redirect('medical_report_detail', pk=report.pk)
        else:
            messages.error(request, "Please fix the errors in the report form.")
    else:
        form = MedicalReportForm(initial=initial)

    return render(request, 'portal/staff_report_form.html', {'form': form})
