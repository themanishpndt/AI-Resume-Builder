# Django Admin Configuration - Complete Database Connection
# This file connects all database models to the admin panel with enhanced UI

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

# Import all models
from resume.models import Profile, Education, Experience, Project, GeneratedResume, CoverLetter


# ==================== RESUME APP ====================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model with rich display."""
    list_display = [
        'get_user_email',
        'get_user_name',
        'location',
        'created_at',
        'updated_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'location', 'summary']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at', 'get_user_link']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'get_user_link')
        }),
        ('Profile Details', {
            'fields': ('career_objective', 'summary', 'skills', 'location')
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'github_url', 'portfolio_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()
    get_user_name.short_description = 'Full Name'
    
    def get_user_link(self, obj):
        """Display a link to the user."""
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    get_user_link.short_description = 'Link to User'


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Admin interface for Education model."""
    list_display = [
        'get_user_email',
        'degree',
        'field_of_study',
        'institution',
        'start_date',
        'end_date',
        'created_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'institution', 'field_of_study', 'degree']
    list_filter = ['degree', 'start_date', 'end_date', 'created_at', 'currently_studying']
    readonly_fields = ['created_at', 'updated_at', 'get_user_link']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'get_user_link')
        }),
        ('Education Details', {
            'fields': ('institution', 'degree', 'field_of_study', 'grade')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'currently_studying')
        }),
        ('Additional Info', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    
    def get_user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    get_user_link.short_description = 'Link to User'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    """Admin interface for Experience model."""
    list_display = [
        'get_user_email',
        'position',
        'company',
        'employment_type',
        'start_date',
        'end_date',
        'currently_working_badge',
        'created_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'company', 'position']
    list_filter = ['employment_type', 'start_date', 'end_date', 'created_at', 'currently_working']
    readonly_fields = ['created_at', 'updated_at', 'get_user_link']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'get_user_link')
        }),
        ('Job Details', {
            'fields': ('company', 'position', 'employment_type', 'currently_working')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date')
        }),
        ('Location & Description', {
            'fields': ('location', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    
    def currently_working_badge(self, obj):
        if obj.currently_working:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Current</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px;">Past</span>'
        )
    currently_working_badge.short_description = 'Status'
    
    def get_user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    get_user_link.short_description = 'Link to User'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Project model."""
    list_display = [
        'get_user_email',
        'title',
        'start_date',
        'end_date',
        'get_tech_count',
        'created_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'title', 'technologies']
    list_filter = ['start_date', 'end_date', 'created_at', 'currently_working']
    readonly_fields = ['created_at', 'updated_at', 'get_user_link']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'get_user_link')
        }),
        ('Project Details', {
            'fields': ('title', 'description', 'start_date', 'end_date', 'currently_working')
        }),
        ('Technical Info', {
            'fields': ('technologies', 'project_url', 'thumbnail')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    
    def get_tech_count(self, obj):
        if obj.technologies:
            count = len(obj.technologies.split(','))
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 3px;">{} tech</span>',
                count
            )
        return '-'
    get_tech_count.short_description = 'Technologies'
    
    def get_user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    get_user_link.short_description = 'Link to User'


@admin.register(GeneratedResume)
class GeneratedResumeAdmin(admin.ModelAdmin):
    """Admin interface for GeneratedResume model."""
    list_display = [
        'get_user_email',
        'title',
        'created_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'title']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'get_user_link']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'get_user_link')
        }),
        ('Resume Details', {
            'fields': ('title',)
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    
    def get_user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    get_user_link.short_description = 'Link to User'


@admin.register(CoverLetter)
class CoverLetterAdmin(admin.ModelAdmin):
    """Admin interface for CoverLetter model."""
    list_display = [
        'get_user_email',
        'title',
        'company_name',
        'position',
        'created_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'title', 'company_name', 'position']
    list_filter = ['created_at', 'company_name']
    readonly_fields = ['created_at', 'get_user_link']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'get_user_link')
        }),
        ('Cover Letter Details', {
            'fields': ('title', 'company_name', 'position', 'job_description')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    
    def get_user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    get_user_link.short_description = 'Link to User'


# ==================== CUSTOMIZE ADMIN SITE ====================

# Customize the admin site header and title
admin.site.site_header = "AI Resume & Portfolio Builder - Administration"
admin.site.site_title = "Admin"
admin.site.index_title = "Welcome to Resume Builder Admin"
