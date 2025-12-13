"""
URL configuration for resume app.
"""
from django.urls import path
from . import views
from .diagnostic_views import config_check, test_email_quick
from .diagnostic_views import debug_last_otp

urlpatterns = [
    # Diagnostic endpoints (for debugging production issues)
    path('api/config-check/', config_check, name='config_check'),
    path('api/test-email/', test_email_quick, name='test_email_quick'),
    path('debug/last-otp/', debug_last_otp, name='debug_last_otp'),
    
    # Password Reset URLs are in core/urls.py (not here to avoid conflicts)
    
    # Home and Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Legal Pages
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    
    # Profile
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Education
    path('education/', views.education_list, name='education_list'),
    path('education/add/', views.education_add, name='education_add'),
    path('education/<int:pk>/edit/', views.education_edit, name='education_edit'),
    path('education/<int:pk>/delete/', views.education_delete, name='education_delete'),
    
    # Experience
    path('experience/', views.experience_list, name='experience_list'),
    path('experience/add/', views.experience_add, name='experience_add'),
    path('experience/<int:pk>/edit/', views.experience_edit, name='experience_edit'),
    path('experience/<int:pk>/delete/', views.experience_delete, name='experience_delete'),
    
    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.project_add, name='project_add'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Resume Generation
    path('generate/', views.generate_resume, name='generate_resume'),
    path('resumes/', views.resume_list, name='resume_list'),
    path('resumes/<int:pk>/', views.resume_view, name='resume_view'),
    path('resumes/<int:pk>/download/', views.resume_download_pdf, name='resume_download_pdf'),
    path('resumes/<int:pk>/delete/', views.resume_delete, name='resume_delete'),
    
    # Templates Gallery
    path('templates/', views.templates_gallery, name='templates_gallery'),
    
    # Cover Letters
    path('cover-letters/generate/', views.generate_cover_letter, name='generate_cover_letter'),
    path('cover-letters/', views.cover_letter_list, name='cover_letter_list'),
    path('cover-letters/<int:pk>/', views.cover_letter_view, name='cover_letter_view'),
    path('cover-letters/<int:pk>/download/', views.cover_letter_download_pdf, name='cover_letter_download_pdf'),
    path('cover-letters/<int:pk>/delete/', views.cover_letter_delete, name='cover_letter_delete'),
    
    # Portfolio
    path('portfolio/', views.portfolio_view, name='portfolio_view'),
    path('portfolio/download/', views.portfolio_download_pdf, name='portfolio_download_pdf'),
    
]
