from django.db import models
from django.conf import settings
from django.core.validators import URLValidator


class Profile(models.Model):
    """
    User profile containing personal information and career details.
    One-to-one relationship with User model.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    career_objective = models.TextField(blank=True, help_text="Your career goal or objective")
    summary = models.TextField(blank=True, help_text="Professional summary or bio")
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    linkedin_url = models.URLField(blank=True, validators=[URLValidator()])
    github_url = models.URLField(blank=True, validators=[URLValidator()])
    portfolio_url = models.URLField(blank=True, validators=[URLValidator()])
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"
    
    def get_skills_list(self):
        """
        Return skills as a list, handling commas within parentheses.
        Splits by comma but respects parentheses grouping.
        """
        if not self.skills:
            return []
        
        skills = []
        current_skill = ""
        paren_depth = 0
        
        for char in self.skills:
            if char == '(':
                paren_depth += 1
                current_skill += char
            elif char == ')':
                paren_depth -= 1
                current_skill += char
            elif char == ',' and paren_depth == 0:
                # Only split on comma if we're not inside parentheses
                skill = current_skill.strip()
                if skill:
                    skills.append(skill)
                current_skill = ""
            else:
                current_skill += char
        
        # Add the last skill
        skill = current_skill.strip()
        if skill:
            skills.append(skill)
        
        return skills


class Education(models.Model):
    """
    Education details for a user.
    Multiple education entries per user.
    """
    DEGREE_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'Ph.D.'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200, help_text="School/University name")
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES)
    field_of_study = models.CharField(max_length=200, help_text="Major/Field of study")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    currently_studying = models.BooleanField(default=False)
    grade = models.CharField(max_length=50, blank=True, help_text="GPA or grade")
    description = models.TextField(blank=True, help_text="Additional details or achievements")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Education'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.get_degree_display()} in {self.field_of_study} at {self.institution}"


class Experience(models.Model):
    """
    Work experience details for a user.
    Multiple experience entries per user.
    """
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('volunteer', 'Volunteer'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200, help_text="Company name")
    position = models.CharField(max_length=200, help_text="Job title/position")
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    currently_working = models.BooleanField(default=False)
    description = models.TextField(help_text="Responsibilities and achievements")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.company}"


class Project(models.Model):
    """
    Project details for a user's portfolio.
    Multiple projects per user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200, help_text="Project name")
    description = models.TextField(help_text="Project description and your role")
    technologies = models.CharField(max_length=500, help_text="Technologies used (comma-separated)")
    project_url = models.URLField(blank=True, validators=[URLValidator()], help_text="Live demo or repository URL")
    thumbnail = models.ImageField(upload_to='project_thumbnails/', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    currently_working = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def get_technologies_list(self):
        """Return technologies as a list"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
        return []


class GeneratedResume(models.Model):
    """
    Stores generated resumes for users.
    """
    TEMPLATE_CHOICES = [
        ('modern', 'Modern Professional'),
        ('classic', 'Classic Traditional'),
        ('creative', 'Creative Bold'),
        ('minimal', 'Minimal Clean'),
        ('executive', 'Executive Premium'),
        ('technical', 'Technical Expert'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generated_resumes')
    title = models.CharField(max_length=200, default="My Resume")
    content = models.TextField(help_text="AI-generated resume content")
    template = models.CharField(
        max_length=50, 
        default='modern', 
        choices=TEMPLATE_CHOICES,
        help_text="Resume template used"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Generated Resume'
        verbose_name_plural = 'Generated Resumes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"


class CoverLetter(models.Model):
    """
    Stores AI-generated cover letters for users.
    """
    TEMPLATE_CHOICES = [
        ('modern', 'Modern Professional'),
        ('classic', 'Classic Traditional'),
        ('creative', 'Creative Bold'),
        ('minimal', 'Minimal Clean'),
        ('executive', 'Executive Premium'),
        ('technical', 'Technical Expert'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cover_letters')
    title = models.CharField(max_length=200, default="My Cover Letter")
    company_name = models.CharField(max_length=200, help_text="Target company name")
    position = models.CharField(max_length=200, help_text="Job position applying for")
    job_description = models.TextField(blank=True, help_text="Job description (optional)")
    content = models.TextField(help_text="AI-generated cover letter content")
    template = models.CharField(
        max_length=50, 
        default='classic',
        choices=TEMPLATE_CHOICES,
        help_text="Template design for PDF generation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cover Letter'
        verbose_name_plural = 'Cover Letters'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.company_name} - {self.user.get_full_name()}"
