from django.db import models
from django.contrib.auth.hashers import make_password, check_password

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
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('D', 'Declined'),
    ]
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    time = models.TimeField()
    available_slot = models.IntegerField()
    owner = models.ForeignKey(Owners, on_delete=models.CASCADE, related_name='jobs')
    booked_by = models.ForeignKey(UserModel, null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"{self.name} - {self.location}"
