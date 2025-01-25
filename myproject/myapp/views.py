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

# def login(request):
#     """Custom login view."""
#     if request.method == 'POST':
#         identifier = request.POST.get('identifier')
#         password = request.POST.get('password')
#
#         if not identifier or not password:
#             messages.error(request, "Both fields are required.")
#             return render(request, 'login.html')  # Change redirect to render
#
#         user = None
#         try:
#             user = UserModel.objects.get(Q(email=identifier) | Q(phone=identifier))
#             is_user_model = True
#         except UserModel.DoesNotExist:
#             try:
#                 user = Owners.objects.get(Q(email=identifier) | Q(phone=identifier))
#                 is_user_model = False
#             except Owners.DoesNotExist:
#                 user = None
#
#         if user:
#             if is_user_model and user.check_password(password):
#                 return redirect("user_home", identifier)
#             elif not is_user_model and check_password(password, user.password):
#                 return redirect("admin_home", identifier)
#
#         messages.error(request, "Invalid email/phone or password.")
#         return render(request, 'login.html')  # Change redirect to render
#
#     return render(request, 'login.html')
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
    jobs = Jobs.objects.filter(location__icontains=location, status='P') if location else Jobs.objects.filter(status='P')
    user =  get_object_or_404(UserModel, id=user_id)
    return render(request, 'browse.html', {'jobs': jobs, 'user': user, 'user_id': user_id})

# Book Job View
def book_job(request, job_id, user_id):
    if request.method == 'POST':
        job = get_object_or_404(Jobs, id=job_id)
        user = get_object_or_404(UserModel, id=user_id)

        if job.booked_by:
            messages.error(request, 'This job has already been booked.')
            return redirect('browse', user_id=user_id)

        if job.available_slot > 0:
            job.booked_by = user
            job.available_slot -= 1
            job.status = 'A'
            job.save()
            messages.success(request, 'Job booked successfully!')
        else:
            messages.error(request, 'No slots available for this job.')

        return redirect('user_home', user_id=user_id)

# Admin Home View
def admin_home(request, user_id):
    user = Owners.objects.filter(id=user_id)
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
    jobs = Jobs.objects.filter(booked_by=user)
    return render(request, 'status.html', {'jobs': jobs, 'user': user})


# def profile(request, email):
#     user = get_object_or_404(UserModel, email=email)
#
#     # Check if the user has any booked job
#     booked_job = Jobs.objects.filter(booked_by=user).first()  # Get the first job booked by the user
#
#     # Pass the booked job status to the template
#     return render(request, 'profile.html', {
#         'user': user,
#         'booked_job': booked_job  # Pass the booked job to the template
#     })
# def user_home(request, email):
#     details = UserModel.objects.filter(email=email)
#     return render(request, 'user_home.html', {"details": details})
#
#
# def browse(request, email):
#     # Get search parameter
#     location = request.GET.get('location', '')
#
#     # Filter jobs based on location if provided
#     if location:
#         jobs = Jobs.objects.filter(location__icontains=location, status='P')
#     else:
#         jobs = Jobs.objects.filter(status='P')  # Only show pending jobs
#
#     user = UserModel.objects.filter(email=email)
#
#     context = {
#         'jobs': jobs,
#         'request': request,
#         'user': user,
#         'email': email
#     }
#     return render(request, 'browse.html', context)
#
#
#
# def book_job(request, job_id,email):
#     if request.method == 'POST':
#         job = get_object_or_404(Jobs, id=job_id)
#         user = get_object_or_404(UserModel, email=email)
#
#         # Check if job is already booked
#         if job.booked_by:
#             messages.error(request, 'This job has already been booked.')
#             return redirect('browse', email=email)
#
#         # Check if slots are available
#         if job.available_slot > 0:
#             # Book the job
#             job.booked_by = user
#             job.available_slot -= 1
#             job.status = 'A'  # Change status to Accepted
#             job.save()
#
#             messages.success(request, 'Job booked successfully!')
#         else:
#             messages.error(request, 'No slots available for this job.')
#
#         return redirect('user_home', email=email)
#
#

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

# def profile_edit(request, email):
#     user = get_object_or_404(UserModel, Q(email__iexact=email))
#
#     if request.method == 'POST':
#         user.name = request.POST.get('name', user.name)
#         user.age = request.POST.get('age', user.age)
#         user.phone = request.POST.get('phone', user.phone)
#         user.place = request.POST.get('location', user.place)
#         if 'photo' in request.FILES:
#             user.photo = request.FILES['photo']
#
#         # Handle job categories
#         categories = request.POST.getlist('job_categories')
#         user.categories = ','.join(categories)
#
#         user.save()
#         messages.success(request, "Profile updated successfully.")
#         return redirect('profile', email=user.email)
#
#     # Pass job categories to the template
#     job_categories = ['Catering', 'Delivery', 'Painting', 'Cleaning', 'Gardening', 'Moving']
#     return render(request, "profile_edit.html", {'user': user, 'job_categories': job_categories})
#
#
# def admin_home(request, email):
#     # Fetch the admin user details using the provided email
#     user = Owners.objects.filter(email=email)
#
#     return render(request, 'admin_home.html', {"user": user})
#     return render(request, 'profile_edit.html', {'user': user})
#
#
# def admin_profile(request, email):
#     user = get_object_or_404(Owners, email=email)  # Get the user by email
#     jobs = Jobs.objects.filter(owner=user)  # Get all jobs for this owner
#
#     completed_jobs = jobs.filter(status='A')  # Filter jobs with 'Accepted' status (completed jobs)
#
#     context = {
#         "user": user,
#         "total_jobs": jobs.count(),
#         "completed_jobs": completed_jobs.count(),
#         "jobs": jobs,  # Pass jobs for display (optional)
#     }
#     return render(request, "admin_profile.html", context)
# def admin_profile_edit(request, email):
#     user = get_object_or_404(Owners, email=email)
#
#     if request.method == 'POST':
#         # Update user details from POST data
#         user.name = request.POST.get('name', user.name)
#         user.phone = request.POST.get('phone', user.phone)
#         user.location = request.POST.get('location', user.location)
#
#         if 'photo' in request.FILES:
#             user.photo = request.FILES['photo']
#
#         # Don't save job categories to the database, just process them
#         selected_categories = request.POST.getlist('job_categories')
#
#         # Do something with selected_categories if needed, like logging or sending an email
#         # But don't save it to the user model
#
#         user.save()
#         messages.success(request, "Profile updated successfully.")
#         return redirect('admin_profile', email=user.email)
#
#     # Display job categories for selection in the form
#     job_categories = ['Catering', 'Delivery', 'Painting', 'Cleaning', 'Gardening', 'Moving']
#     return render(request, "profile_edit.html", {'user': user, 'job_categories': job_categories})
#
# def status(request, email):
#     users = Owners.objects.get(email=email)
#     jobs = Jobs.objects.filter(owner=users).order_by('date', 'time')
#     user = Owners.objects.filter(email=email)
#     return render(request, "status.html", {"user": user, "jobs": jobs})
#

# from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt
#
# # Store submitted data temporarily
# data_store = {}
#
#
# @csrf_exempt
# def addslot(request, email):
#     if request.method == 'POST':
#         # Get the owner instance
#         owner = Owners.objects.get(email=email)
#
#         # Create new job
#         job = Jobs.objects.create(
#             name=request.POST.get('name'),
#             category=request.POST.get('category'),
#             location=request.POST.get('location'),
#             amount=request.POST.get('amount'),
#             date=request.POST.get('date'),
#             time=request.POST.get('time'),
#             available_slot=request.POST.get('available_slot'),
#             owner=owner,
#             status='P'  # Default status is Pending
#         )
#
#         return redirect('admin_home', email=email)
#
#     return render(request, 'addslot.html', {'user': [{'email': email}]})
#
#

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