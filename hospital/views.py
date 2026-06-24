from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import linebreaks
from django.utils import timezone
from django.utils.html import escape
from .forms import AppointmentForm, ConsultationForm, EmailLoginForm, PrescriptionForm, RegisterForm, TestimonialForm
from .models import Appointment, Banner, Doctor, Prescription, SiteSetting, Speciality, Testimonial, WhyChoose


def home(request):
    banners = Banner.objects.filter(is_active=True)
    specialities = Speciality.objects.filter(is_active=True, show_on_home=True)[:6]
    why_choose = WhyChoose.objects.filter(is_active=True)[:6]
    featured_doctors = Doctor.objects.filter(is_available=True, is_featured=True)[:4]
    testimonials = Testimonial.objects.filter(is_active=True, show_on_home=True)[:10]
    testimonial_initial = {}
    if request.user.is_authenticated:
        testimonial_initial['patient_name'] = request.user.get_full_name() or request.user.username
    testimonial_form = TestimonialForm(initial=testimonial_initial)
    return render(request, 'hospital/home.html', {
        'banners': banners,
        'specialities': specialities,
        'why_choose': why_choose,
        'featured_doctors': featured_doctors,
        'testimonials': testimonials,
        'testimonial_form': testimonial_form,
    })


def submit_testimonial(request):
    if request.method != 'POST':
        return redirect('/#testimonials')

    form = TestimonialForm(request.POST, request.FILES)
    if form.is_valid():
        testimonial = form.save(commit=False)
        testimonial.is_active = False
        testimonial.show_on_home = True
        testimonial.save()
        messages.success(request, 'Thank you for sharing your experience. Your testimonial is waiting for admin approval.')
    else:
        messages.error(request, 'Please check the testimonial form and submit again. Rating must be between 1 and 5.')
    return redirect('/#testimonials')

def specialists(request):
    query = request.GET.get('q', '').strip()
    speciality_id = request.GET.get('speciality', '').strip()
    doctors = Doctor.objects.select_related('speciality').filter(is_available=True)

    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(degree__icontains=query) |
            Q(designation__icontains=query) |
            Q(speciality__name__icontains=query)
        )

    if speciality_id:
        doctors = doctors.filter(speciality_id=speciality_id)

    specialities = Speciality.objects.filter(is_active=True)
    return render(request, 'hospital/specialists.html', {
        'doctors': doctors,
        'specialities': specialities,
        'query': query,
        'selected_speciality': speciality_id,
    })


def doctor_detail(request, slug):
    doctor = get_object_or_404(Doctor.objects.select_related('speciality'), slug=slug, is_available=True)
    form = AppointmentForm(initial={
        'name': request.user.get_full_name() if request.user.is_authenticated else '',
        'email': request.user.email if request.user.is_authenticated else '',
    })
    return render(request, 'hospital/doctor_detail.html', {'doctor': doctor, 'form': form})


def make_appointment(request, doctor_id=None):
    doctor = None
    if doctor_id:
        doctor = get_object_or_404(Doctor, id=doctor_id, is_available=True)

    initial = {}
    if request.user.is_authenticated:
        initial = {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            if request.user.is_authenticated:
                appointment.user = request.user
            appointment.save()
            messages.success(request, 'Your appointment request has been submitted successfully.')
            return redirect('my_appointments' if request.user.is_authenticated else 'home')
    else:
        form = AppointmentForm(initial=initial)

    return render(request, 'hospital/appointment.html', {'form': form, 'doctor': doctor})


@login_required
def online_consultation(request):
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.user = request.user
            consultation.save()
            messages.success(request, 'Your online consultation request has been submitted.')
            return redirect('my_appointments')
    else:
        form = ConsultationForm()
    return render(request, 'hospital/consultation.html', {'form': form})


@login_required
def prescriptions(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.user = request.user
            if not prescription.patient_name:
                prescription.patient_name = request.user.get_full_name() or request.user.username
            if not prescription.issued_date:
                prescription.issued_date = timezone.localdate()
            prescription.save()
            messages.success(request, 'Prescription saved successfully.')
            return redirect('prescriptions')
    else:
        initial = {'patient_name': request.user.get_full_name() or request.user.username}
        form = PrescriptionForm(initial=initial)

    user_prescriptions = request.user.prescriptions.select_related('doctor', 'doctor__speciality')
    return render(request, 'hospital/prescriptions.html', {
        'form': form,
        'prescriptions': user_prescriptions,
    })


def _safe_paragraph(value, empty='Not specified'):
    text = value or empty
    return linebreaks(escape(text))


@login_required
def download_prescription(request, prescription_id):
    prescription = get_object_or_404(
        Prescription.objects.select_related('doctor', 'doctor__speciality', 'user'),
        id=prescription_id
    )
    if prescription.user != request.user and not request.user.is_staff:
        raise Http404('Prescription not found')

    setting = SiteSetting.objects.order_by('-created_at').first()
    doctor = prescription.doctor
    issued_date = prescription.issued_date or prescription.created_at.date()

    doctor_name = doctor.name if doctor else 'Doctor not assigned'
    doctor_degree = doctor.degree if doctor else '-'
    doctor_speciality = doctor.speciality.name if doctor and doctor.speciality else '-'
    doctor_phone = doctor.phone if doctor and doctor.phone else (setting.general_line if setting else '-')
    doctor_designation = doctor.designation if doctor and doctor.designation else doctor_speciality
    hospital_name = setting.site_name if setting else 'Assunta Hospital'
    hospital_phone = setting.general_line if setting else '+603-7872 3000'
    hospital_email = setting.email if setting else 'info@example.com'
    hospital_address = setting.address if setting else '123 Main Street'

    file_link = ''
    if prescription.file:
        file_link = f'<p><strong>Attached File:</strong> {escape(prescription.file.name.split("/")[-1])}</p>'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{escape(prescription.title)} - Prescription</title>
<style>
    body {{ font-family: Arial, Helvetica, sans-serif; background:#f4f6f8; margin:0; padding:30px; color:#1f2937; }}
    .sheet {{ max-width:850px; margin:0 auto; background:#fff; border:1px solid #e5e7eb; box-shadow:0 8px 30px rgba(0,0,0,.08); }}
    .header {{ display:flex; justify-content:space-between; gap:20px; align-items:flex-start; border-bottom:5px solid #ef4136; padding:28px 34px; }}
    .brand h1 {{ color:#ef4136; margin:0 0 6px; font-size:30px; }}
    .brand p, .doctor-box p, .patient-grid p {{ margin:4px 0; }}
    .doctor-box {{ text-align:right; font-size:14px; }}
    .doctor-box h2 {{ margin:0 0 6px; font-size:22px; color:#111827; }}
    .badge {{ display:inline-block; background:#e8f8ef; color:#15803d; padding:7px 12px; border-radius:999px; font-weight:700; margin-top:8px; }}
    .body {{ padding:30px 34px; }}
    .title-row {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }}
    .title-row h2 {{ margin:0; font-size:26px; }}
    .patient-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:12px 25px; background:#f9fafb; padding:18px; border-radius:8px; border:1px solid #e5e7eb; }}
    .section {{ margin-top:24px; }}
    .section h3 {{ color:#ef4136; border-bottom:1px solid #e5e7eb; padding-bottom:8px; margin-bottom:12px; }}
    .rx {{ font-size:38px; font-family:Georgia,serif; color:#15803d; float:left; margin-right:12px; line-height:1; }}
    .box {{ background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:16px; line-height:1.7; min-height:60px; }}
    .footer {{ display:flex; justify-content:space-between; align-items:flex-end; gap:30px; padding:24px 34px 34px; }}
    .signature {{ text-align:center; min-width:240px; }}
    .line {{ border-top:1px solid #111827; margin-top:55px; padding-top:8px; }}
    .note {{ font-size:12px; color:#6b7280; }}
    @media print {{ body {{ background:#fff; padding:0; }} .sheet {{ box-shadow:none; border:0; }} }}
</style>
</head>
<body>
<div class="sheet">
    <div class="header">
        <div class="brand">
            <h1>{escape(hospital_name)}</h1>
            <p>{escape(hospital_address)}</p>
            <p>Phone: {escape(hospital_phone)} | Email: {escape(hospital_email)}</p>
        </div>
        <div class="doctor-box">
            <h2>{escape(doctor_name)}</h2>
            <p>{escape(doctor_degree)}</p>
            <p>{escape(doctor_designation)}</p>
            <p>Specialist: {escape(doctor_speciality)}</p>
            <p>Mobile/Phone: {escape(doctor_phone)}</p>
            <span class="badge">Verified Prescription</span>
        </div>
    </div>
    <div class="body">
        <div class="title-row">
            <h2>{escape(prescription.title)}</h2>
            <strong>Date: {issued_date.strftime('%d %b %Y')}</strong>
        </div>
        <div class="patient-grid">
            <p><strong>Patient Name:</strong> {escape(prescription.display_patient_name)}</p>
            <p><strong>Patient Email:</strong> {escape(prescription.user.email or '-')}</p>
            <p><strong>Age:</strong> {escape(str(prescription.patient_age or '-'))}</p>
            <p><strong>Gender:</strong> {escape(prescription.patient_gender or '-')}</p>
            <p><strong>Follow-up Date:</strong> {prescription.follow_up_date.strftime('%d %b %Y') if prescription.follow_up_date else '-'}</p>
            <p><strong>Prescription ID:</strong> RX-{prescription.id:05d}</p>
        </div>
        <div class="section">
            <h3>Diagnosis</h3>
            <div class="box">{_safe_paragraph(prescription.diagnosis)}</div>
        </div>
        <div class="section">
            <h3><span class="rx">℞</span> Medicines / Dosage</h3>
            <div class="box">{_safe_paragraph(prescription.medicines)}</div>
        </div>
        <div class="section">
            <h3>Instructions</h3>
            <div class="box">{_safe_paragraph(prescription.instructions)}</div>
        </div>
        <div class="section">
            <h3>Additional Notes</h3>
            <div class="box">{_safe_paragraph(prescription.note, 'No additional note.')}{file_link}</div>
        </div>
    </div>
    <div class="footer">
        <p class="note">This prescription was generated from the hospital appointment system. Please consult the hospital if you need verification.</p>
        <div class="signature">
            <div class="line">{escape(doctor_name)}<br>{escape(doctor_speciality)}</div>
        </div>
    </div>
</div>
</body>
</html>'''

    response = HttpResponse(html, content_type='text/html')
    filename = f'prescription_RX-{prescription.id:05d}.html'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def my_appointments(request):
    appointments = Appointment.objects.select_related('doctor').filter(user=request.user)
    return render(request, 'hospital/my_appointments.html', {'appointments': appointments})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'hospital/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data['user'])
            messages.success(request, 'Login successful.')
            return redirect('home')
    else:
        form = EmailLoginForm()
    return render(request, 'hospital/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')
