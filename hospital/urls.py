from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('specialists/', views.specialists, name='specialists'),
    path('doctor/<slug:slug>/', views.doctor_detail, name='doctor_detail'),
    path('appointment/', views.make_appointment, name='appointment'),
    path('appointment/<int:doctor_id>/', views.make_appointment, name='doctor_appointment'),
    path('consultation/', views.online_consultation, name='consultation'),
    path('testimonials/submit/', views.submit_testimonial, name='submit_testimonial'),
    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path('prescriptions/<int:prescription_id>/download/', views.download_prescription, name='download_prescription'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
