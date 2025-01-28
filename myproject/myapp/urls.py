from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('login/', views.login, name='login'),  # Login page
    path('signup/', views.signup, name='signup'),  # Sign-up page
    path('logout/', views.logout_view, name='logout'),  # Logout functionality
    path('profile/<int:user_id>/', views.profile, name='profile'),  # Profile page
    path('user_home/<int:user_id>/', views.user_home, name='user_home'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('browse/<int:user_id>/', views.browse, name='browse'),
    path('browse2/', views.browse2, name='browse2'),
    path('book_job/<int:job_id>/<int:user_id>/', views.book_job, name='book_job'),
    path('jobs_list/', views.job_list, name='job_list'),
    path('owner_jobs/', views.owner_jobs, name='owner_jobs'),
    path('manage_booking/<int:job_id>/<str:action>/', views.manage_booking, name='manage_booking'),
    path('admin-signup/', views.admin_signup, name='admin_signup'),
    path('admin_home/<int:user_id>/', views.admin_home, name='admin_home'),
    path('admin_profile/<int:user_id>/', views.admin_profile, name='admin_profile'),
    path('admin_profile_edit/<int:user_id>/', views.admin_profile_edit, name='admin_profile_edit'),
    path('profile_edit/<int:user_id>/', views.profile_edit, name='profile_edit'),
    path('addslot/<int:user_id>/', views.addslot, name='addslot'),
    path('status/<int:user_id>/', views.status, name='status'),
    path('categories/<str:name>/', views.categories, name='categories'),
    path('job_status/', views.job_status, name='job_status'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('change-booking-status/<int:booking_id>/', views.change_booking_status, name='change_booking_status'),
    path('remove-job/<int:job_id>/', views.remove_job, name='remove_job'),
]
# urlpatterns = [
#     path('',views.home,name='home'),  # Home page
#     path('login/', views.login, name='login'),  # Login page
#     path('signup/', views.signup, name='signup'),  # Sign-up page
#     path('logout/', views.logout_view, name='logout'),  # Logout functionality
#     path('profile/<str:email>/', views.profile, name='profile'),  # Profile page
#     path('user_home/<email>/', views.user_home, name='user_home'),
#     path('logout_view/', views.logout_view, name='logout_view'),
#     path('browse/<email>/', views.browse, name='browse'),
#     path('browse2/', views.browse2, name='browse2'),
#     path('book_job/<int:job_id>/', views.book_job, name='book_job'),
#     path('jobs_list/', views.job_list, name='job_list'),
#     path('owner_jobs/', views.owner_jobs, name='owner_jobs'),
#     path('manage_booking/<int:job_id>/<str:action>/', views.manage_booking, name='manage_booking'),
#     path('admin-signup/', views.admin_signup, name='admin_signup'),
#     path('admin_home/<email>/', views.admin_home, name='admin_home'),
#     path('admin_profile/<email>/', views.admin_profile, name='admin_profile'),
#     path('admin_profile_edit/<email>/', views.admin_profile_edit, name='admin_profile_edit'),
#     path('profile_edit/<email>/', views.profile_edit, name='profile_edit'),
#     path('addslot/<email>/', views.addslot, name='addslot'),
#     path('status/<email>/', views.status, name='status'),
#     # path('forms/<email>/', views.forms, name='forms'),
#     path('categories/<name>', views.categories, name='categories'),
#     # path('forms/', views.forms, name='forms'),
#     path('book-job/<int:job_id>/<str:email>/', views.book_job, name='book_job'),
#
#
# ]
