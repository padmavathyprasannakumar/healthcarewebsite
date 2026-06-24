from django.contrib import admin
from .models import (
    Appointment, Banner, Doctor, OnlineConsultation, Prescription,
    SiteSetting, Speciality, Testimonial, WhyChoose
)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'general_line', 'emergency_line', 'whatsapp', 'email')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('title', 'subtitle')


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_on_home', 'is_active', 'order')
    list_editable = ('show_on_home', 'is_active', 'order')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Speciality Information', {
            'fields': ('name', 'description')
        }),
        ('Home Page Icon', {
            'fields': ('icon', 'icon_emoji'),
            'description': 'Upload speciality icon images here. These are used on the Key Specialities section, not doctor profile photos.'
        }),
        ('Display Settings', {
            'fields': ('show_on_home', 'is_active', 'order')
        }),
    )


@admin.register(WhyChoose)
class WhyChooseAdmin(admin.ModelAdmin):
    list_display = ('icon_text', 'number', 'title', 'is_active', 'order')
    list_editable = ('is_active', 'order')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'speciality', 'degree', 'phone', 'is_available', 'is_featured')
    list_filter = ('speciality', 'is_available', 'is_featured')
    search_fields = ('name', 'degree', 'designation', 'speciality__name', 'phone')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Doctor Profile', {
            'fields': ('name', 'slug', 'speciality', 'degree', 'designation', 'profile_image', 'bio')
        }),
        ('Contact and Appointment', {
            'fields': ('phone', 'email', 'room_no', 'earliest_appointment', 'consultation_fee')
        }),
        ('Display Settings', {
            'fields': ('is_available', 'is_featured')
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'doctor', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('name', 'email', 'phone', 'doctor__name')
    list_editable = ('status',)


@admin.register(OnlineConsultation)
class OnlineConsultationAdmin(admin.ModelAdmin):
    list_display = ('problem_title', 'user', 'doctor', 'preferred_date', 'status', 'created_at')
    list_filter = ('status', 'preferred_date')
    search_fields = ('problem_title', 'user__username', 'doctor__name')
    list_editable = ('status',)


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'patient_name', 'doctor', 'issued_date', 'created_at')
    list_filter = ('doctor', 'issued_date', 'created_at')
    search_fields = ('title', 'user__username', 'user__email', 'patient_name', 'doctor__name', 'doctor__phone')
    autocomplete_fields = ('user', 'doctor')
    fieldsets = (
        ('Prescription Owner', {
            'fields': ('user', 'doctor', 'title', 'issued_date')
        }),
        ('Patient Details', {
            'fields': ('patient_name', 'patient_age', 'patient_gender')
        }),
        ('Prescription Content', {
            'fields': ('diagnosis', 'medicines', 'instructions', 'follow_up_date', 'note')
        }),
        ('Optional Uploaded File', {
            'fields': ('file',)
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'patient_role', 'rating', 'show_on_home', 'is_active', 'order', 'created_at')
    list_editable = ('rating', 'show_on_home', 'is_active', 'order')
    list_filter = ('is_active', 'show_on_home', 'rating')
    search_fields = ('patient_name', 'patient_role', 'message')
    fieldsets = (
        ('Patient Story', {
            'fields': ('patient_name', 'patient_role', 'patient_image', 'message', 'rating')
        }),
        ('Display Settings', {
            'fields': ('show_on_home', 'is_active', 'order')
        }),
    )
