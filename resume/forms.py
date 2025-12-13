from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Profile, Education, Experience, Project
from .countries_data import COUNTRIES, STATES_BY_COUNTRY


class ProfileForm(forms.ModelForm):
    """
    Form for creating and updating user profile.
    """
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/Province',
            'id': 'id_state'
        })
    )
    country = forms.ChoiceField(
        choices=COUNTRIES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_country',
            'onchange': 'updateStates()'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['career_objective', 'summary', 'skills', 'linkedin_url', 
                  'github_url', 'portfolio_url', 'location']
        widgets = {
            'career_objective': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Seeking a challenging position as a Software Engineer...'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief professional summary highlighting your key strengths...'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Python, Django, JavaScript, React, PostgreSQL (comma-separated)'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourusername'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourportfolio.com'
            }),
            'location': forms.HiddenInput(),  # Hidden, will be populated from city + country
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Split location into city, state, and country if it exists
        if self.instance and self.instance.location:
            # Try to parse "City, State, Country" or "City, Country"
            location_parts = [part.strip() for part in self.instance.location.split(',')]
            if len(location_parts) == 3:
                self.initial['city'] = location_parts[0]
                self.initial['state'] = location_parts[1]
                self.initial['country'] = location_parts[2]
            elif len(location_parts) == 2:
                self.initial['city'] = location_parts[0]
                # Check if second part is a country or state
                if location_parts[1] in [c[0] for c in COUNTRIES]:
                    self.initial['country'] = location_parts[1]
                else:
                    self.initial['state'] = location_parts[1]
            else:
                self.initial['city'] = self.instance.location
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Combine city, state, and country into location
        city = self.cleaned_data.get('city', '').strip()
        state = self.cleaned_data.get('state', '').strip()
        country = self.cleaned_data.get('country', '').strip()
        
        location_parts = []
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if country:
            location_parts.append(country)
        
        instance.location = ', '.join(location_parts)
        
        if commit:
            instance.save()
        return instance


class EducationForm(forms.ModelForm):
    """
    Form for adding and editing education entries.
    """
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 
                  'end_date', 'currently_studying', 'grade', 'description']
        labels = {
            'institution': 'Institution',
            'degree': 'Degree',
            'field_of_study': 'Field of Study',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'currently_studying': 'Currently Studying',
            'grade': 'Grade',
            'description': 'Description',
        }
        widgets = {
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'University/School Name'
            }),
            'degree': forms.Select(attrs={'class': 'form-select'}),
            'field_of_study': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'currently_studying': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'grade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 3.8 GPA or 85%'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Relevant coursework, achievements, honors...'
            }),
        }


class ExperienceForm(forms.ModelForm):
    """
    Form for adding and editing work experience entries.
    """
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/Province',
            'id': 'id_experience_state'
        })
    )
    country = forms.ChoiceField(
        choices=COUNTRIES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_experience_country',
            'onchange': 'updateExperienceStates()'
        })
    )
    
    class Meta:
        model = Experience
        fields = ['company', 'position', 'employment_type', 'location', 
                  'start_date', 'end_date', 'currently_working', 'description']
        labels = {
            'company': 'Company',
            'position': 'Position',
            'employment_type': 'Employment Type',
            'location': 'Location',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'currently_working': 'Currently Working',
            'description': 'Description',
        }
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job Title'
            }),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.HiddenInput(),  # Hidden, will be populated from city + state + country
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'currently_working': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your responsibilities and achievements...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Split location into city, state, and country if it exists
        if self.instance and self.instance.location:
            # Try to parse "City, State, Country" or "City, Country"
            location_parts = [part.strip() for part in self.instance.location.split(',')]
            if len(location_parts) == 3:
                self.initial['city'] = location_parts[0]
                self.initial['state'] = location_parts[1]
                self.initial['country'] = location_parts[2]
            elif len(location_parts) == 2:
                self.initial['city'] = location_parts[0]
                # Check if second part is a country or state
                if location_parts[1] in [c[0] for c in COUNTRIES]:
                    self.initial['country'] = location_parts[1]
                else:
                    self.initial['state'] = location_parts[1]
            else:
                self.initial['city'] = self.instance.location
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Combine city, state, and country into location
        city = self.cleaned_data.get('city', '').strip()
        state = self.cleaned_data.get('state', '').strip()
        country = self.cleaned_data.get('country', '').strip()
        
        location_parts = []
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if country:
            location_parts.append(country)
        
        instance.location = ', '.join(location_parts)
        
        if commit:
            instance.save()
        return instance


class ProjectForm(forms.ModelForm):
    """
    Form for adding and editing project entries.
    """
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies', 'project_url', 
                  'thumbnail', 'start_date', 'end_date', 'currently_working']
        labels = {
            'title': 'Title',
            'description': 'Description',
            'technologies': 'Technologies',
            'project_url': 'Project URL',
            'thumbnail': 'Thumbnail',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'currently_working': 'Currently Working',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Project Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the project, your role, and key achievements...'
            }),
            'technologies': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Django, React, PostgreSQL (comma-separated)'
            }),
            'project_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourusername/project or live demo URL'
            }),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'currently_working': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CoverLetterForm(forms.Form):
    """
    Form for generating AI-powered cover letters.
    """
    company_name = forms.CharField(
        max_length=200,
        required=True,
        label='Company Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Google, Microsoft, Amazon'
        }),
        help_text='Name of the company you are applying to'
    )
    
    position = forms.CharField(
        max_length=200,
        required=True,
        label='Position',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Software Engineer, Data Analyst, Product Manager'
        }),
        help_text='Job title/position you are applying for'
    )
    
    job_description = forms.CharField(
        required=False,
        label='Job Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Paste the job description here (optional but recommended for better results)'
        }),
        help_text='Optional: Paste the job description to get a more tailored cover letter'
    )
