from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteSetting(TimeStampedModel):
    site_name = models.CharField(max_length=120, default='Assunta Hospital')
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    general_line = models.CharField(max_length=50, default='+603-7872 3000')
    emergency_line = models.CharField(max_length=50, default='+603-7877 9999')
    whatsapp = models.CharField(max_length=50, default='+603-7872 3100')
    email = models.EmailField(default='info@example.com')
    address = models.CharField(max_length=255, default='123 Main Street')
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    footer_text = models.CharField(max_length=255, default='© 2026 Company Name. All Rights Reserved.')

    def __str__(self):
        return self.site_name


class Banner(TimeStampedModel):
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class Speciality(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(
        upload_to='specialities/',
        blank=True,
        null=True,
        help_text='Upload speciality icon only, for example brain, heart, liver icon. Do not upload doctor photo here.'
    )
    icon_emoji = models.CharField(max_length=20, blank=True, default='✚', help_text='Fallback icon if no image is uploaded.')
    description = models.TextField(blank=True)
    show_on_home = models.BooleanField(default=True, help_text='Show this speciality in Key Specialities on the home page.')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Specialities'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class WhyChoose(TimeStampedModel):
    icon_text = models.CharField(max_length=20, default='★', help_text='Use emoji or icon text, e.g. ★, ♥, 🏥')
    number = models.CharField(max_length=30, help_text='Example: 71, 245, 100+')
    title = models.CharField(max_length=100, help_text='Example: Years of Experience')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.number} {self.title}'


class Doctor(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL, null=True, related_name='doctors')
    degree = models.CharField(max_length=255, help_text='Example: MBBS, FRCP')
    designation = models.CharField(max_length=120, blank=True, help_text='Example: Consultant Cardiologist')
    profile_image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    room_no = models.CharField(max_length=40, blank=True)
    bio = models.TextField(blank=True)
    earliest_appointment = models.CharField(max_length=100, blank=True, help_text='Example: Feb 22, 2:30PM')
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Doctor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                count += 1
                slug = f'{base_slug}-{count}'
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('doctor_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Appointment(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    appointment_date = models.DateField()
    appointment_time = models.TimeField(blank=True, null=True)
    symptoms = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        doctor_name = self.doctor.name if self.doctor else 'General Appointment'
        return f'{self.name} - {doctor_name}'


class OnlineConsultation(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    problem_title = models.CharField(max_length=150)
    description = models.TextField()
    preferred_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.problem_title


class Prescription(TimeStampedModel):
    GENDER_CHOICES = [
        ('', 'Not specified'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150, default='Medical Prescription')
    patient_name = models.CharField(max_length=120, blank=True)
    patient_age = models.PositiveIntegerField(blank=True, null=True)
    patient_gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, default='')
    diagnosis = models.TextField(blank=True)
    medicines = models.TextField(blank=True, help_text='Write medicine name, dosage, frequency, and duration.')
    instructions = models.TextField(blank=True, help_text='Advice, precautions, diet, rest, review date, etc.')
    follow_up_date = models.DateField(blank=True, null=True)
    issued_date = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to='prescriptions/', blank=True, null=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def display_patient_name(self):
        if self.patient_name:
            return self.patient_name
        return self.user.get_full_name() or self.user.username


class Testimonial(TimeStampedModel):
    # Migration 0003 intentionally removed updated_at from this table.
    # Keeping this override prevents Django admin from querying a missing
    # hospital_testimonial.updated_at column in existing SQLite databases.
    updated_at = None

    patient_name = models.CharField(max_length=100)
    patient_role = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Example: Patient, Heart Patient, Surgery Patient'
    )
    patient_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    message = models.TextField()
    rating = models.PositiveIntegerField(default=5, help_text='Enter rating from 1 to 5')
    show_on_home = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['order', '-created_at']

    @property
    def star_display(self):
        rating = max(0, min(int(self.rating or 0), 5))
        return '★' * rating + '☆' * (5 - rating)

    def __str__(self):
        return self.patient_name
