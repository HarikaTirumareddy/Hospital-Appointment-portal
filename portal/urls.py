from django.urls import path
from . import views

urlpatterns = [
    # Public & Doctors
    path('', views.home_view, name='home'),
    path('doctors/', views.doctor_list_view, name='doctor_list'),
    path('doctors/<int:pk>/', views.doctor_detail_view, name='doctor_detail'),
    
    # Patient Authentication
    path('register/', views.patient_register_view, name='patient_register'),
    path('login/', views.patient_login_view, name='patient_login'),
    path('logout/', views.patient_logout_view, name='patient_logout'),
    
    # Patient Portal
    path('dashboard/', views.patient_dashboard_view, name='patient_dashboard'),
    path('profile/edit/', views.patient_profile_edit_view, name='patient_profile_edit'),
    path('book-appointment/', views.book_appointment_view, name='book_appointment'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment_view, name='cancel_appointment'),
    path('reports/<int:pk>/', views.medical_report_detail_view, name='medical_report_detail'),
    
    # AJAX / Real-Time API for slots
    path('api/booked-slots/', views.api_booked_slots, name='api_booked_slots'),
    
    # Staff / Admin Portal
    path('staff/', views.staff_dashboard_view, name='staff_dashboard'),
    path('staff/appointments/<int:pk>/status/', views.staff_update_status_view, name='staff_update_status'),
    path('staff/doctors/', views.staff_doctors_view, name='staff_doctors'),
    path('staff/doctors/add/', views.staff_doctor_create_view, name='staff_doctor_create'),
    path('staff/doctors/<int:pk>/edit/', views.staff_doctor_edit_view, name='staff_doctor_edit'),
    path('staff/doctors/<int:pk>/delete/', views.staff_doctor_delete_view, name='staff_doctor_delete'),
    path('staff/reports/add/', views.staff_report_create_view, name='staff_report_create'),
]
