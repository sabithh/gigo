from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from .models import *
import re
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse

def home(request):
    """Home page view."""
    return render(request, 'home.html', )

def signup(request):
    """Sign-up view."""
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Form validation
        if not identifier or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, 'signup.html')  # Change redirect to render

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')  # Change redirect to render

        # Determine if the identifier is an email or phone number
        if '@' in identifier:  # Email validation
            if UserModel.objects.filter(email=identifier).exists():
                messages.error(request, "Email already registered.")
                return render(request, 'signup.html')  # Change redirect to render
            user = UserModel(email=identifier, password=make_password(password))
        else:  # Phone validation
            if UserModel.objects.filter(phone=identifier).exists():
                messages.error(request, "Phone number already registered.")
                return render(request, 'signup.html')  # Change redirect to render
            user = UserModel(phone=identifier, password=make_password(password))

        # Save user details
        try:
            user.name = request.POST.get('name', 'User')  # Default name
            user.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, "An error occurred while creating your account.")
            return render(request, 'signup.html')

    return render(request, 'signup.html')

def login(request):
    """Custom login view."""
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # Email or phone
        password = request.POST.get('password')

        if not identifier or not password:
            messages.error(request, "Both fields are required.")
            return render(request, 'login.html')

        user = None
        is_user_model = False
        try:
            # Attempt to find the user in UserModel
            user = UserModel.objects.get(Q(email=identifier) | Q(phone=identifier))
            is_user_model = True
        except UserModel.DoesNotExist:
            try:
                # Attempt to find the user in Owners
                user = Owners.objects.get(Q(email=identifier) | Q(phone=identifier))
                is_user_model = False
            except Owners.DoesNotExist:
                user = None

        if user:
            # Validate the password and redirect with user_id
            if is_user_model and user.check_password(password):
                return redirect("user_home", user_id=user.id)  # Ensure user.id is passed
            elif not is_user_model and check_password(password, user.password):
                return redirect("admin_home", user_id=user.id)  # Ensure user.id is passed

        # If authentication fails
        messages.error(request, "Invalid email/phone or password.")
        return render(request, 'login.html')

    return render(request, 'login.html')

def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')
# User Profile View
def profile(request, user_id):
    user = get_object_or_404(UserModel, id=user_id)
    booked_job = Jobs.objects.filter(booked_by=user).first()
    return render(request, 'profile.html', {
        'user': user,
        'booked_job': booked_job,
    })

# User Home View
def user_home(request, user_id):
    user = get_object_or_404(UserModel, id=user_id)
    return render(request, 'user_home.html', {"user": user})

# Browse Jobs View
def browse(request, user_id):
    location = request.GET.get('location', '')
    jobs = Jobs.objects.filter(location__icontains=location)
    if location:
        jobs = jobs.filter(location__icontains=location)

    # Annotate jobs with booking information
    for job in jobs:
        job.user_has_booked = job.bookings.filter(user_id=user_id).exists()
        job.remaining_slots = job.get_remaining_slots()

    user = get_object_or_404(UserModel, id=user_id)
    return render(request, 'browse.html', {
        'jobs': jobs,
        'user': user,
        'user_id': user_id
    })

# Book Job View
def book_job(request, job_id, user_id):
    if request.method == 'POST':
        job = get_object_or_404(Jobs, id=job_id)
        user = get_object_or_404(UserModel, id=user_id)

        # Check if user already has a booking for this job
        existing_booking = JobBooking.objects.filter(job=job, user=user).exists()
        if existing_booking:
            messages.error(request, 'You have already booked this job.')
            return redirect('browse', user_id=user_id)

        # Check if slots are available
        if job.get_remaining_slots() > 0:
            JobBooking.objects.create(
                job=job,
                user=user,
                status='P'
            )
            messages.success(request, 'Job booking request submitted successfully!')
        else:
            messages.error(request, 'No slots available for this job.')

        return redirect('user_home', user_id=user_id)
# Admin Home View
def admin_home(request,user_id):
    user = get_object_or_404(Owners, id=user_id)
    return render(request, 'admin_home.html', {"user": user})

# Admin Profile View
def admin_profile(request, user_id):
    user = get_object_or_404(Owners, id=user_id)
    return render(request, 'admin_profile.html', {'user': user})

# Admin Profile Edit View
def admin_profile_edit(request, user_id):
    user = get_object_or_404(Owners, id=user_id)
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('admin_profile', user_id=user_id)
    return render(request, 'admin_profile_edit.html', {'user': user})

# User Profile Edit View
def profile_edit(request, user_id):
    user = get_object_or_404(UserModel, id=user_id)
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile', user_id=user_id)
    return render(request, 'profile_edit.html', {'user': user})

# Add Slot View
def addslot(request, user_id):
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        slots = request.POST.get('slots')
        job = get_object_or_404(Jobs, id=job_id)

        job.available_slot += int(slots)
        job.save()

        messages.success(request, 'Slots added successfully!')
        return redirect('admin_home', user_id=user_id)
    return render(request, 'addslot.html', {'user_id': user_id})

# Job Status View
def status(request, user_id):
    user = get_object_or_404(UserModel, id=user_id)
    bookings = JobBooking.objects.filter(user=user).select_related('job')
    return render(request, 'status.html', {'bookings': bookings, 'user': user})


def job_list(request):
    jobs = Jobs.objects.filter(booked_by__isnull=True)  # Show only available jobs
    return render(request, 'browse.html', {'jobs': jobs})
def browse2(request):
    jobs = Jobs.objects.filter(booked_by__isnull=True)  # Show only available jobs
    return render(request, 'browse2.html', {'jobs': jobs})

def owner_jobs(request):
    owner = request.user.owners  # Assuming the owner is authenticated
    jobs = owner.jobs.all()
    return render(request, 'owner_jobs.html', {'jobs': jobs})

def manage_booking(request, job_id, action):
    job = get_object_or_404(Jobs, id=job_id, owner=request.user.owners)

    if action == 'accept':
        job.status = 'A'
        messages.success(request, f"Booking for {job.name} has been accepted.")
    elif action == 'decline':
        job.status = 'D'
        job.booked_by = None
        messages.success(request, f"Booking for {job.name} has been declined.")

    job.save()
    return redirect('owner_jobs')
def admin_signup(request):
    if request.method == "POST":
        # Retrieve form data
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate passwords
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'admin_signup.html')

        # Strong password validation
        strong_password_regex = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        )
        if not re.match(strong_password_regex, password):
            messages.error(
                request,
                "Password must include at least one uppercase letter, one lowercase letter, one digit, and one special character.",
            )
            return render(request, 'admin_signup.html')

        try:
            # Check if the user already exists (email as username)
            if Owners.objects.filter(email=identifier).exists():
                messages.error(request, "This email or phone number is already in use.")
                return render(request, 'admin_signup.html')

            # Save new admin user
            user = Owners.objects.create(
                email=identifier,
                password=make_password(password),
                # Grant admin privileges
            )
            messages.success(request, "Admin account created successfully!")
            return redirect('login')  # Adjust the redirect as per your URLs

        except IntegrityError:
            messages.error(request, "An error occurred. Please try again.")
            return render(request, 'admin_signup.html')

    return render(request, 'admin_signup.html')


def categories(request, name):
    # Get today's date in the project's timezone
    today = timezone.now().date()

    # Generate dates for next 7 days
    dates = []
    for i in range(7):
        current_date = today + timedelta(days=i)
        date_dict = {
            'day': 'Today' if i == 0 else current_date.strftime('%a'),
            'date': current_date.strftime('%b %d'),
            'full_date': current_date
        }
        dates.append(date_dict)

    # Filter jobs by category and date
    jobs = Jobs.objects.filter(
        category=name,
        date__in=[date['full_date'] for date in dates]
    )

    return render(request, 'categories.html', {
        'jobs': jobs,
        'category': name,
        'dates': dates
    })

def update_job_status(request, job_id, action):
    job = get_object_or_404(Jobs, id=job_id)

    if action == 'accept':
        job.status = 'A'  # Accepted
    elif action == 'decline':
        job.status = 'D'  # Declined
    else:
        return HttpResponse("Invalid action.", status=400)

    job.save()
    return redirect('job_list')  # Replace 'job_list' with your actual job listing page URL name

def job_status(request):
    """View to display the logged-in user's job status."""
    user = request.user
    if not user.is_authenticated:
        messages.error(request, "You need to log in first.")
        return redirect('login')

    # Fetch jobs booked by the logged-in user's ID
    jobs = Jobs.objects.filter(booked_by_id=user.id)

    return render(request, 'job_status.html', {'jobs': jobs})


def cancel_booking(request, booking_id):
    booking = get_object_or_404(JobBooking, id=booking_id)
    if booking.status == 'P':
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
    else:
        messages.error(request, "Cannot cancel an accepted or declined booking.")
    return redirect('job_status')


def change_booking_status(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(JobBooking, id=booking_id)
        new_status = request.POST.get('status')

        if new_status in ['A', 'D']:
            if new_status == 'A' and booking.job.get_remaining_slots() <= 0:
                messages.error(request, "No slots available for this job.")
            else:
                booking.status = new_status
                booking.save()
                messages.success(request, f"Booking status updated to {booking.get_status_display()}.")
        else:
            messages.error(request, "Invalid status update.")

    return redirect('status')

def remove_job(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(Jobs, id=job_id)
        job.delete()
        messages.success(request, "Job removed successfully.")
    return redirect('status')  # Redirect to the job status page