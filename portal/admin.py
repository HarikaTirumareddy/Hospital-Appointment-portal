from django.contrib import admin
from .models import Department, Doctor, PatientProfile, Appointment, MedicalReport, Patient

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_class', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'specialization', 'experience_years', 'consultation_fee', 'room_number', 'is_available')
    list_filter = ('department', 'is_available')
    search_fields = ('name', 'specialization', 'qualifications', 'email', 'phone')
    list_editable = ('is_available',)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'user', 'phone', 'gender', 'blood_group', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone', 'address')
    list_filter = ('gender', 'blood_group')

    def get_patient_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_patient_name.short_description = "Patient Name"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_name', 'doctor', 'appointment_date', 'time_slot', 'status_badge', 'created_at')
    list_filter = ('status', 'appointment_date', 'doctor__department')
    search_fields = ('patient__username', 'patient__first_name', 'patient__last_name', 'doctor__name', 'symptoms_or_reason')
    date_hierarchy = 'appointment_date'
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    def patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username
    patient_name.short_description = "Patient"

    def status_badge(self, obj):
        colors = {
            'Pending': 'orange',
            'Confirmed': 'blue',
            'Completed': 'green',
            'Cancelled': 'red'
        }
        from django.utils.html import format_html
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = "Status"

    @admin.action(description="Mark selected appointments as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Appointment.STATUS_CONFIRMED)

    @admin.action(description="Mark selected appointments as Completed")
    def mark_completed(self, request, queryset):
        queryset.update(status=Appointment.STATUS_COMPLETED)

    @admin.action(description="Mark selected appointments as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status=Appointment.STATUS_CANCELLED)


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'doctor', 'report_type', 'has_file', 'created_at')
    list_filter = ('report_type', 'created_at', 'doctor__department')
    search_fields = ('title', 'patient__username', 'patient__first_name', 'doctor__name', 'diagnosis')

    def has_file(self, obj):
        return bool(obj.report_file)
    has_file.boolean = True
    has_file.short_description = "File Attached"
