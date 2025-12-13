from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from .models import Profile, Education, Experience, Project, GeneratedResume, CoverLetter
from .forms import ProfileForm, EducationForm, ExperienceForm, ProjectForm, CoverLetterForm
from .services import AIResumeGenerator
from .utils import generate_pdf_from_html, format_resume_for_pdf, create_portfolio_html
from users.forms import UserProfileForm
from .countries_data import STATES_BY_COUNTRY
import json


def home(request):
    """
    Homepage view - shows landing page for all users.
    """
    return render(request, 'resume/home.html')


def terms_of_service(request):
    """
    Terms of Service page.
    """
    return render(request, 'legal/terms.html')


def privacy_policy(request):
    """
    Privacy Policy page.
    """
    return render(request, 'legal/privacy.html')


@login_required
def dashboard(request):
    """
    User dashboard showing overview of profile data.
    """
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Get all user data
    educations = Education.objects.filter(user=request.user)
    experiences = Experience.objects.filter(user=request.user)
    projects = Project.objects.filter(user=request.user)
    generated_resumes = GeneratedResume.objects.filter(user=request.user).order_by('-created_at')[:5]
    cover_letters = CoverLetter.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'educations': educations,
        'experiences': experiences,
        'projects': projects,
        'generated_resumes': generated_resumes,
        'cover_letters': cover_letters,
        'education_count': educations.count(),
        'experience_count': experiences.count(),
        'project_count': projects.count(),
        'resume_count': GeneratedResume.objects.filter(user=request.user).count(),
        'cover_letter_count': CoverLetter.objects.filter(user=request.user).count(),
    }
    
    return render(request, 'resume/dashboard.html', context)


@login_required
def profile_edit(request):
    """
    Edit user profile and personal information.
    """
    from .countries_data import STATES_BY_COUNTRY
    import json
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'states_json': json.dumps(STATES_BY_COUNTRY),
    }
    
    return render(request, 'resume/profile_edit.html', context)


# Education Views
@login_required
def education_list(request):
    """
    List all education entries.
    """
    educations = Education.objects.filter(user=request.user)
    return render(request, 'resume/education_list.html', {'educations': educations})


@login_required
def education_add(request):
    """
    Add new education entry.
    """
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            messages.success(request, 'Education added successfully!')
            return redirect('education_list')
    else:
        form = EducationForm()
    
    return render(request, 'resume/education_form.html', {'form': form, 'action': 'Add'})


@login_required
def education_edit(request, pk):
    """
    Edit existing education entry.
    """
    education = get_object_or_404(Education, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education updated successfully!')
            return redirect('education_list')
    else:
        form = EducationForm(instance=education)
    
    return render(request, 'resume/education_form.html', {'form': form, 'action': 'Edit'})


@login_required
def education_delete(request, pk):
    """
    Delete education entry.
    """
    education = get_object_or_404(Education, pk=pk, user=request.user)
    
    if request.method == 'POST':
        education.delete()
        messages.success(request, 'Education deleted successfully!')
        return redirect('education_list')
    
    return render(request, 'resume/education_confirm_delete.html', {'education': education})


# Experience Views
@login_required
def experience_list(request):
    """
    List all experience entries.
    """
    experiences = Experience.objects.filter(user=request.user)
    return render(request, 'resume/experience_list.html', {'experiences': experiences})


@login_required
def experience_add(request):
    """
    Add new experience entry.
    """
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.user = request.user
            experience.save()
            messages.success(request, 'Experience added successfully!')
            return redirect('experience_list')
    else:
        form = ExperienceForm()
    
    context = {
        'form': form,
        'action': 'Add',
        'states_json': json.dumps(STATES_BY_COUNTRY)
    }
    return render(request, 'resume/experience_form.html', context)


@login_required
def experience_edit(request, pk):
    """
    Edit existing experience entry.
    """
    experience = get_object_or_404(Experience, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, 'Experience updated successfully!')
            return redirect('experience_list')
    else:
        form = ExperienceForm(instance=experience)
    
    context = {
        'form': form,
        'action': 'Edit',
        'states_json': json.dumps(STATES_BY_COUNTRY)
    }
    return render(request, 'resume/experience_form.html', context)


@login_required
def experience_delete(request, pk):
    """
    Delete experience entry.
    """
    experience = get_object_or_404(Experience, pk=pk, user=request.user)
    
    if request.method == 'POST':
        experience.delete()
        messages.success(request, 'Experience deleted successfully!')
        return redirect('experience_list')
    
    return render(request, 'resume/experience_confirm_delete.html', {'experience': experience})


# Project Views
@login_required
def project_list(request):
    """
    List all project entries.
    """
    projects = Project.objects.filter(user=request.user)
    return render(request, 'resume/project_list.html', {'projects': projects})


@login_required
def project_add(request):
    """
    Add new project entry.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, 'Project added successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'resume/project_form.html', {'form': form, 'action': 'Add'})


@login_required
def project_edit(request, pk):
    """
    Edit existing project entry.
    """
    project = get_object_or_404(Project, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'resume/project_form.html', {'form': form, 'action': 'Edit'})


@login_required
def project_delete(request, pk):
    """
    Delete project entry.
    """
    project = get_object_or_404(Project, pk=pk, user=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')
    
    return render(request, 'resume/project_confirm_delete.html', {'project': project})


# AI Resume Generation Views
@login_required
def generate_resume(request):
    """
    Generate AI-powered resume with template selection.
    """
    # Get selected template from query parameter or POST
    selected_template = request.GET.get('template', request.POST.get('template', 'modern'))
    
    if request.method == 'POST':
        template_id = request.POST.get('template', 'modern')
        
        try:
            generator = AIResumeGenerator(request.user)
            success, content, error = generator.generate_resume(template=template_id)
            
            if success and content:
                # Save generated resume with template info
                template_name = dict([(t['id'], t['name']) for t in [
                    {'id': 'modern', 'name': 'Modern Professional'},
                    {'id': 'classic', 'name': 'Classic Traditional'},
                    {'id': 'creative', 'name': 'Creative Bold'},
                    {'id': 'minimal', 'name': 'Minimal Clean'},
                    {'id': 'executive', 'name': 'Executive Premium'},
                    {'id': 'technical', 'name': 'Technical Expert'},
                ]]).get(template_id, 'Modern Professional')
                
                resume = GeneratedResume.objects.create(
                    user=request.user,
                    title=f"Resume - {request.user.get_full_name()} ({template_name})",
                    content=content,
                    template=template_id
                )
                messages.success(request, f'Resume generated successfully using {template_name} template!')
                return redirect('resume_view', pk=resume.pk)
            else:
                # If generation failed, show error
                error_msg = error if error else 'Unknown error occurred'
                messages.error(request, f'Error generating resume: {error_msg}. Please ensure you have completed your profile.')
                return redirect('generate_resume')
                
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}. Please try again or contact support.')
            return redirect('generate_resume')
    
    # Get user data for template
    profile, created = Profile.objects.get_or_create(user=request.user)
    educations = Education.objects.filter(user=request.user)
    experiences = Experience.objects.filter(user=request.user)
    projects = Project.objects.filter(user=request.user)
    
    # Calculate profile completeness
    completeness_parts = [
        bool(profile.summary),
        educations.exists(),
        experiences.exists(),
        projects.exists(),
    ]
    filled_count = sum(completeness_parts)
    completeness_percentage = (filled_count / 4) * 100
    
    # Available templates
    available_templates = [
        {
            'id': 'modern',
            'name': 'Modern Professional',
            'icon': 'bi-stars',
            'description': 'Clean and modern design with color accents',
            'category': 'modern'
        },
        {
            'id': 'classic',
            'name': 'Classic Traditional',
            'icon': 'bi-briefcase',
            'description': 'Traditional and elegant corporate format',
            'category': 'traditional'
        },
        {
            'id': 'creative',
            'name': 'Creative Bold',
            'icon': 'bi-palette',
            'description': 'Eye-catching design for creative fields',
            'category': 'creative'
        },
        {
            'id': 'minimal',
            'name': 'Minimal Clean',
            'icon': 'bi-circle',
            'description': 'Minimalist design focusing on content',
            'category': 'modern'
        },
        {
            'id': 'executive',
            'name': 'Executive Premium',
            'icon': 'bi-award',
            'description': 'Premium design for senior positions',
            'category': 'traditional'
        },
        {
            'id': 'technical',
            'name': 'Technical Expert',
            'icon': 'bi-code-slash',
            'description': 'Structured format for technical roles',
            'category': 'modern'
        },
    ]
    
    context = {
        'profile': profile,
        'educations': educations,
        'experiences': experiences,
        'projects': projects,
        'completeness_percentage': int(completeness_percentage),
        'available_templates': available_templates,
        'selected_template': selected_template,
    }
    
    return render(request, 'resume/generate_resume.html', context)


@login_required
def resume_view(request, pk):
    """
    View generated resume.
    """
    resume = get_object_or_404(GeneratedResume, pk=pk, user=request.user)
    return render(request, 'resume/resume_view.html', {'resume': resume})


@login_required
def resume_download_pdf(request, pk):
    """
    Download resume as PDF with template styling.
    """
    resume = get_object_or_404(GeneratedResume, pk=pk, user=request.user)
    
    # Format content for PDF
    html_content = format_resume_for_pdf(request.user, resume.content)
    
    # Get template from resume or default to modern
    template = getattr(resume, 'template', 'modern')
    
    # Generate and return PDF with template styling
    return generate_pdf_from_html(
        html_content,
        filename=f"resume_{request.user.username}_{template}.pdf",
        template=template
    )


@login_required
def resume_list(request):
    """
    List all generated resumes.
    """
    resumes = GeneratedResume.objects.filter(user=request.user)
    return render(request, 'resume/resume_list.html', {'resumes': resumes})


@login_required
def resume_delete(request, pk):
    """
    Delete generated resume.
    """
    resume = get_object_or_404(GeneratedResume, pk=pk, user=request.user)
    
    if request.method == 'POST':
        resume.delete()
        messages.success(request, 'Resume deleted successfully!')
        return redirect('resume_list')
    
    return render(request, 'resume/resume_confirm_delete.html', {'resume': resume})


@login_required
def portfolio_view(request):
    """
    View user's portfolio.
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    educations = Education.objects.filter(user=request.user)
    experiences = Experience.objects.filter(user=request.user)
    projects = Project.objects.filter(user=request.user)
    
    context = {
        'profile': profile,
        'educations': educations,
        'experiences': experiences,
        'projects': projects,
    }
    
    return render(request, 'resume/portfolio.html', context)


@login_required
def portfolio_download_pdf(request):
    """
    Download portfolio as PDF with template styling.
    """
    # Get template from query parameter or default to modern
    template = request.GET.get('template', 'modern')
    
    html_content = create_portfolio_html(request.user)
    
    return generate_pdf_from_html(
        html_content,
        filename=f"portfolio_{request.user.username}_{template}.pdf",
        template=template
    )


# Theme switching removed: site now uses fixed light theme and no server-side endpoint is needed.


# ==================== COVER LETTER VIEWS ====================

@login_required
def generate_cover_letter(request):
    """
    Generate AI-powered cover letter based on user profile and job details.
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CoverLetterForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data['company_name']
            position = form.cleaned_data['position']
            job_description = form.cleaned_data.get('job_description', '')
            template = request.POST.get('template', 'classic')
            
            try:
                # Initialize AI service with user
                ai_generator = AIResumeGenerator(user=request.user)
                
                # Gather user data
                user_data = {
                    'name': request.user.get_full_name() or request.user.email,
                    'email': request.user.email,
                    'profile': {
                        'summary': profile.summary or '',
                        'skills': profile.get_skills_list() if hasattr(profile, 'get_skills_list') else [],
                        'career_objective': profile.career_objective or '',
                    },
                    'education': list(Education.objects.filter(user=request.user).values()),
                    'experience': list(Experience.objects.filter(user=request.user).values()),
                    'projects': list(Project.objects.filter(user=request.user).values()),
                    'company_name': company_name,
                    'position': position,
                    'job_description': job_description,
                }
                
                # Generate cover letter
                cover_letter_content = ai_generator.generate_cover_letter(user_data)
                
                # Save to database
                cover_letter = CoverLetter.objects.create(
                    user=request.user,
                    title=f"Cover Letter - {company_name} - {position}",
                    company_name=company_name,
                    position=position,
                    job_description=job_description,
                    content=cover_letter_content,
                    template=template
                )
                
                messages.success(request, f'Cover letter generated successfully for {company_name}!')
                return redirect('cover_letter_view', pk=cover_letter.pk)
                
            except Exception as e:
                messages.error(request, f'Error generating cover letter: {str(e)}')
    else:
        form = CoverLetterForm()
    
    context = {
        'form': form,
        'profile': profile,
        'education_count': Education.objects.filter(user=request.user).count(),
        'experience_count': Experience.objects.filter(user=request.user).count(),
        'project_count': Project.objects.filter(user=request.user).count(),
    }
    
    return render(request, 'resume/generate_cover_letter.html', context)


@login_required
def cover_letter_list(request):
    """
    List all cover letters for the current user.
    """
    cover_letters = CoverLetter.objects.filter(user=request.user)
    
    context = {
        'cover_letters': cover_letters,
    }
    
    return render(request, 'resume/cover_letter_list.html', context)


@login_required
def cover_letter_view(request, pk):
    """
    View a specific cover letter.
    """
    cover_letter = get_object_or_404(CoverLetter, pk=pk, user=request.user)
    
    context = {
        'cover_letter': cover_letter,
    }
    
    return render(request, 'resume/cover_letter_view.html', context)


@login_required
def cover_letter_download_pdf(request, pk):
    """
    Download cover letter as PDF with template styling.
    """
    from html import escape
    import re
    
    cover_letter = get_object_or_404(CoverLetter, pk=pk, user=request.user)
    
    # Get template from cover letter object or query parameter, default to classic
    template = request.GET.get('template', cover_letter.template if hasattr(cover_letter, 'template') and cover_letter.template else 'classic')
    
    # Format the cover letter content - convert line breaks to paragraphs
    content_paragraphs = []
    for paragraph in cover_letter.content.split('\n\n'):
        paragraph = paragraph.strip()
        if paragraph:
            # Replace single line breaks with <br> within paragraphs
            paragraph = paragraph.replace('\n', '<br>')
            # Handle bold text
            paragraph = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', paragraph)
            content_paragraphs.append(f'<p>{escape(paragraph)}</p>')
    
    formatted_content = ''.join(content_paragraphs)
    
    # Create HTML for PDF
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Cover Letter - {escape(cover_letter.company_name)}</title>
    </head>
    <body>
        <div class="header">
            <h1>{escape(request.user.get_full_name())}</h1>
            <p class="contact-info">{escape(request.user.email)}</p>
            <p class="date">{cover_letter.created_at.strftime('%B %d, %Y')}</p>
        </div>
        <div class="section">
            <p><strong>{escape(cover_letter.company_name)}</strong><br>
            <strong>Re: {escape(cover_letter.position)}</strong></p>
        </div>
        <div class="content">
            {formatted_content}
        </div>
    </body>
    </html>
    """
    
    return generate_pdf_from_html(
        html_content,
        filename=f"cover_letter_{cover_letter.company_name}_{cover_letter.position}.pdf",
        template=template
    )


@login_required
def cover_letter_delete(request, pk):
    """
    Delete a cover letter.
    """
    cover_letter = get_object_or_404(CoverLetter, pk=pk, user=request.user)
    
    if request.method == 'POST':
        cover_letter.delete()
        messages.success(request, 'Cover letter deleted successfully!')
        return redirect('cover_letter_list')
    
    context = {
        'cover_letter': cover_letter,
    }
    
    return render(request, 'resume/cover_letter_confirm_delete.html', context)


@login_required
def templates_gallery(request):
    """
    Display resume templates gallery for users to browse and preview.
    """
    # Define available resume templates with their details
    templates = [
        {
            'id': 'modern',
            'name': 'Modern Professional',
            'category': 'modern',
            'description': 'Clean and modern design perfect for tech and creative professionals',
            'preview_image': 'images/template-modern.png',
            'features': ['Two-column layout', 'Color accents', 'Icon support', 'ATS-friendly'],
            'best_for': ['Software Engineers', 'Designers', 'Marketing Professionals'],
        },
        {
            'id': 'classic',
            'name': 'Classic Traditional',
            'category': 'traditional',
            'description': 'Traditional and elegant format suitable for corporate and formal industries',
            'preview_image': 'images/template-classic.png',
            'features': ['Single-column layout', 'Professional typography', 'Traditional format', 'Highly readable'],
            'best_for': ['Finance', 'Legal', 'Academia', 'Healthcare'],
        },
        {
            'id': 'creative',
            'name': 'Creative Bold',
            'category': 'creative',
            'description': 'Eye-catching design for creative fields and portfolios',
            'preview_image': 'images/template-creative.png',
            'features': ['Bold colors', 'Creative layout', 'Portfolio section', 'Modern typography'],
            'best_for': ['Graphic Designers', 'Artists', 'Content Creators', 'UX Designers'],
        },
        {
            'id': 'minimal',
            'name': 'Minimal Clean',
            'category': 'modern',
            'description': 'Minimalist design focusing on content and readability',
            'preview_image': 'images/template-minimal.png',
            'features': ['Clean lines', 'Minimal design', 'High readability', 'Space efficient'],
            'best_for': ['All Industries', 'Entry Level', 'Career Changers'],
        },
        {
            'id': 'executive',
            'name': 'Executive Premium',
            'category': 'traditional',
            'description': 'Premium design for senior positions and executive roles',
            'preview_image': 'images/template-executive.png',
            'features': ['Sophisticated layout', 'Leadership focus', 'Achievement highlights', 'Premium feel'],
            'best_for': ['C-Level Executives', 'Senior Management', 'Directors'],
        },
        {
            'id': 'technical',
            'name': 'Technical Expert',
            'category': 'modern',
            'description': 'Structured format ideal for technical and engineering roles',
            'preview_image': 'images/template-technical.png',
            'features': ['Skills matrix', 'Project highlights', 'Technical details', 'Certifications section'],
            'best_for': ['Engineers', 'Data Scientists', 'IT Professionals', 'DevOps'],
        },
    ]
    
    import json
    context = {
        'templates': templates,
        'templates_json': json.dumps(templates),
        'page_title': 'Resume Templates',
    }
    
    return render(request, 'resume/templates_gallery.html', context)
