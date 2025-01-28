from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
class UserModel(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    password = models.CharField(max_length=128)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    rating = models.FloatField(default=0.0, blank=True, null=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email

class Owners(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True,null=True)
    photo = models.ImageField(upload_to='owner_photos/', blank=True, null=True)
    location = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    def __str__(self):
        return self.email


class Jobs(models.Model):
    CATEGORY_CHOICES = [
        ('catering', 'Catering'),
        ('painting', 'Painting'),
        ('delivery', 'Delivery'),
        ('packing', 'Packing'),
        ('cleaning', 'Cleaning'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    date = models.DateField()
    time = models.TimeField()
    available_slot = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)]
    )
    owner = models.ForeignKey(
        'Owners',
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    avg_working_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Average working hours for this job"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_remaining_slots(self):
        booked_slots = self.bookings.count()
        return max(0, self.available_slot - booked_slots)

    def get_total_working_hours(self):
        """Calculate total working hours for all booked slots"""
        return self.avg_working_hours * self.available_slot

    def is_upcoming(self):
        """Check if the job is in the future"""
        job_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return job_datetime > timezone.now()

    def get_total_earnings(self):
        """Calculate total potential earnings from all slots"""
        return self.amount * self.available_slot

    def get_booked_earnings(self):
        """Calculate earnings from booked slots"""
        booked_slots = self.bookings.filter(status='A').count()
        return self.amount * booked_slots

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['date']),
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return f"{self.name} - {self.location} ({self.date})"


class JobBooking(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('D', 'Declined'),
        ('C', 'Completed'),
        ('X', 'Cancelled'),
    ]

    job = models.ForeignKey(
        Jobs,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    user = models.ForeignKey(
        'UserModel',
        on_delete=models.CASCADE,
        related_name='job_bookings'
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='P'
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    actual_hours_worked = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    completion_date = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )

    def save(self, *args, **kwargs):
        if self.status == 'C' and not self.completion_date:
            self.completion_date = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Job Booking'
        verbose_name_plural = 'Job Bookings'
        unique_together = ['job', 'user']
        ordering = ['-booking_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['booking_date']),
        ]

    def __str__(self):
        return f"{self.user} - {self.job} ({self.get_status_display()})"