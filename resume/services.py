"""
AI service for generating resumes and cover letters using OpenAI API.
"""
from openai import OpenAI
from django.conf import settings
from .models import Profile, Education, Experience, Project


class AIResumeGenerator:
    """
    Service class for generating AI-powered resumes and cover letters.
    """
    
    def __init__(self, user):
        self.user = user
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        
        if self.api_key:
            try:
                # Initialize OpenAI client with just the API key
                # The client will handle all configuration
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                # If client initialization fails, log it but don't crash
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self.client = None
    
    def _gather_user_data(self):
        """
        Collect all user data from database.
        """
        data = {
            'name': self.user.get_full_name(),
            'email': self.user.email,
            'phone': self.user.phone or '',
            'profile': None,
            'education': [],
            'experience': [],
            'projects': []
        }
        
        # Get profile
        try:
            profile = Profile.objects.get(user=self.user)
            data['profile'] = {
                'career_objective': profile.career_objective,
                'summary': profile.summary,
                'skills': profile.get_skills_list(),
                'location': profile.location,
                'linkedin': profile.linkedin_url,
                'github': profile.github_url,
                'portfolio': profile.portfolio_url,
            }
        except Profile.DoesNotExist:
            pass
        
        # Get education
        educations = Education.objects.filter(user=self.user)
        for edu in educations:
            data['education'].append({
                'institution': edu.institution,
                'degree': edu.get_degree_display(),
                'field': edu.field_of_study,
                'start_date': edu.start_date.strftime('%B %Y'),
                'end_date': edu.end_date.strftime('%B %Y') if edu.end_date else 'Present',
                'grade': edu.grade,
                'description': edu.description,
            })
        
        # Get experience
        experiences = Experience.objects.filter(user=self.user)
        for exp in experiences:
            data['experience'].append({
                'company': exp.company,
                'position': exp.position,
                'type': exp.get_employment_type_display(),
                'location': exp.location,
                'start_date': exp.start_date.strftime('%B %Y'),
                'end_date': exp.end_date.strftime('%B %Y') if exp.end_date else 'Present',
                'description': exp.description,
            })
        
        # Get projects
        projects = Project.objects.filter(user=self.user)
        for proj in projects:
            data['projects'].append({
                'title': proj.title,
                'description': proj.description,
                'technologies': proj.get_technologies_list(),
                'url': proj.project_url,
                'start_date': proj.start_date.strftime('%B %Y'),
                'end_date': proj.end_date.strftime('%B %Y') if proj.end_date else 'Present',
            })
        
        return data
    
    def _build_prompt(self, data, document_type='resume', template='modern'):
        """
        Build the AI prompt from user data.
        """
        # Template-specific instructions
        template_instructions = {
            'modern': 'Use a clean, modern format with clear section headers. Add color accents (suggest using blue). Use bullet points effectively.',
            'classic': 'Use a traditional, formal format with serif fonts. Keep it professional and conservative. Use proper business letter formatting.',
            'creative': 'Use a bold, eye-catching design. Be creative with layout. Suggest using two columns or unique section layouts.',
            'minimal': 'Use a minimalist, clean design. Focus on white space and readability. Keep formatting simple and elegant.',
            'executive': 'Use a premium, sophisticated format suitable for C-level positions. Emphasize leadership and strategic achievements.',
            'technical': 'Use a structured format with clear technical sections. Include skills matrix and technical project details prominently.'
        }
        
        template_style = template_instructions.get(template, template_instructions['modern'])
        
        if document_type == 'resume':
            prompt = f"""Create a professional, well-structured resume for the following candidate. 

STYLE REQUIREMENTS: {template_style}

Format it with clear sections and use professional language that highlights key achievements.

PERSONAL INFORMATION:
Name: {data['name']}
Email: {data['email']}
Phone: {data['phone']}
Location: {data['profile']['location'] if data['profile'] else ''}

"""
            if data['profile']:
                if data['profile']['career_objective']:
                    prompt += f"CAREER OBJECTIVE:\n{data['profile']['career_objective']}\n\n"
                
                if data['profile']['summary']:
                    prompt += f"PROFESSIONAL SUMMARY:\n{data['profile']['summary']}\n\n"
                
                if data['profile']['skills']:
                    prompt += f"SKILLS:\n{', '.join(data['profile']['skills'])}\n\n"
            
            if data['education']:
                prompt += "EDUCATION:\n"
                for edu in data['education']:
                    prompt += f"- {edu['degree']} in {edu['field']}, {edu['institution']} ({edu['start_date']} - {edu['end_date']})\n"
                    if edu['grade']:
                        prompt += f"  Grade: {edu['grade']}\n"
                    if edu['description']:
                        prompt += f"  {edu['description']}\n"
                prompt += "\n"
            
            if data['experience']:
                prompt += "WORK EXPERIENCE:\n"
                for exp in data['experience']:
                    prompt += f"- {exp['position']} at {exp['company']} ({exp['start_date']} - {exp['end_date']})\n"
                    prompt += f"  {exp['description']}\n"
                prompt += "\n"
            
            if data['projects']:
                prompt += "PROJECTS:\n"
                for proj in data['projects']:
                    prompt += f"- {proj['title']}\n"
                    prompt += f"  Technologies: {', '.join(proj['technologies'])}\n"
                    prompt += f"  {proj['description']}\n"
                prompt += "\n"
            
            prompt += """\n
IMPORTANT OUTPUT FORMAT:
Generate the resume as clean HTML using these CSS classes:
- Wrap header in <div class="header">
- Use <h1> for name, <h2> for section headers, <h3> for job titles/degrees
- Use <div class="contact-info"> for contact details
- Wrap each section in <div class="section">
- Wrap each job/education entry in <div class="item">
- Use <p class="company"> for company names and <p class="institution"> for schools
- Use <p class="date-range"> for date ranges
- Use <ul class="skills-list"> with <li> for skills
- Use regular <ul> and <li> for bullet points in descriptions

Do NOT include markdown formatting (no #, **, etc.). Generate pure HTML only.
Example structure:
<div class="header">
<h1>Name</h1>
<div class="contact-info">email | phone | location</div>
</div>
<div class="section">
<h2>Section Name</h2>
<div class="item">
<h3>Title</h3>
<p class="company">Company</p>
<p class="date-range">Date Range</p>
<p>Description</p>
</div>
</div>
"""
        
        else:  # cover letter
            prompt = f"""Write a professional cover letter for {data['name']} based on the following information:

{data['profile']['summary'] if data['profile'] and data['profile']['summary'] else 'No summary provided'}

Key Skills: {', '.join(data['profile']['skills']) if data['profile'] and data['profile']['skills'] else 'Not specified'}

Recent Experience:
"""
            if data['experience']:
                for exp in data['experience'][:2]:  # Use top 2 experiences
                    prompt += f"- {exp['position']} at {exp['company']}: {exp['description'][:200]}...\n"
            
            prompt += "\nWrite a compelling cover letter that highlights their strengths and enthusiasm for new opportunities."
        
        return prompt
    
    def generate_resume(self, template='modern'):
        """
        Generate a resume using AI with specified template.
        Args:
            template: Template ID (modern, classic, creative, minimal, executive, technical)
        Returns tuple: (success: bool, content: str, error: str)
        """
        if not self.api_key or not self.client:
            return self._generate_fallback_resume(template=template)
        
        try:
            data = self._gather_user_data()
            prompt = self._build_prompt(data, 'resume', template=template)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer. Generate resumes as clean HTML using CSS classes (header, section, item, contact-info, company, institution, date-range, skills-list). Never use markdown. Only output HTML tags and content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            
            content = response.choices[0].message.content.strip()
            return True, content, None
            
        except Exception as e:
            return False, None, str(e)
    
    def generate_cover_letter(self, user_data=None, job_title=None, company=None):
        """
        Generate a cover letter using AI.
        Args:
            user_data: Dictionary with user data (if provided, uses this instead of gathering)
            job_title: Job position (deprecated, use user_data['position'])
            company: Company name (deprecated, use user_data['company_name'])
        Returns: str with cover letter content or raises exception
        """
        # For backward compatibility
        if user_data is None:
            data = self._gather_user_data()
            if job_title:
                data['position'] = job_title
            if company:
                data['company_name'] = company
        else:
            data = user_data
        
        # Use fallback if no API key
        if not self.api_key or not self.client:
            return self._generate_fallback_cover_letter(data)
        
        try:
            # Build cover letter prompt
            prompt = f"""Write a professional cover letter for:

Name: {data.get('name', 'the candidate')}
Position: {data.get('position', 'the position')}
Company: {data.get('company_name', 'the company')}

Candidate Background:
- Career Objective: {data.get('profile', {}).get('career_objective', 'Not provided')}
- Summary: {data.get('profile', {}).get('summary', 'Not provided')}
- Key Skills: {', '.join(data.get('profile', {}).get('skills', []))}

"""
            
            if data.get('job_description'):
                prompt += f"\nJob Description:\n{data['job_description']}\n"
            
            if data.get('experience'):
                prompt += f"\nRelevant Experience: {len(data['experience'])} positions\n"
            
            if data.get('education'):
                prompt += f"Education: {len(data['education'])} degrees/certifications\n"
            
            prompt += "\nPlease write a compelling, personalized cover letter that:"
            prompt += "\n1. Addresses the specific position and company"
            prompt += "\n2. Highlights relevant skills and experiences"
            prompt += "\n3. Shows enthusiasm for the role"
            prompt += "\n4. Is professional and concise (3-4 paragraphs)"
            prompt += "\n5. Does NOT include address or date (we'll add those)"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional career coach specializing in writing compelling, personalized cover letters that help candidates stand out."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            
            content = response.choices[0].message.content.strip()
            return content
            
        except Exception as e:
            # Return fallback on error
            return self._generate_fallback_cover_letter(data)
    
    def _generate_fallback_resume(self, template='modern'):
        """
        Generate a basic resume without AI when API key is not available.
        Creates properly formatted HTML that matches template designs.
        """
        data = self._gather_user_data()
        
        # Template-specific HTML generation
        if template == 'modern':
            content = self._generate_modern_html(data)
        elif template == 'classic':
            content = self._generate_classic_html(data)
        elif template == 'creative':
            content = self._generate_creative_html(data)
        elif template == 'minimal':
            content = self._generate_minimal_html(data)
        elif template == 'executive':
            content = self._generate_executive_html(data)
        elif template == 'technical':
            content = self._generate_technical_html(data)
        else:
            content = self._generate_modern_html(data)
        
        return True, content, None
    
    def _generate_modern_html(self, data):
        """Generate Modern template HTML"""
        html = '<div class="header">\n'
        html += f'<h1>{data["name"] if data["name"] else "Your Name"}</h1>\n'
        
        # Contact info
        contact = []
        if data['email']:
            contact.append(f'📧 {data["email"]}')
        if data['phone']:
            contact.append(f'📱 {data["phone"]}')
        if data['profile'] and data['profile']['location']:
            contact.append(f'📍 {data["profile"]["location"]}')
        if data['profile'] and data['profile']['linkedin']:
            contact.append(f'🔗 {data["profile"]["linkedin"]}')
        
        if contact:
            html += f'<div class="contact-info">{" | ".join(contact)}</div>\n'
        html += '</div>\n\n'
        
        # Professional Summary
        if data['profile'] and data['profile']['summary']:
            html += '<div class="section">\n'
            html += '<h2>Professional Summary</h2>\n'
            html += f'<p>{data["profile"]["summary"]}</p>\n'
            html += '</div>\n\n'
        
        # Experience
        if data['experience']:
            html += '<div class="section">\n'
            html += '<h2>Work Experience</h2>\n'
            for exp in data['experience']:
                html += '<div class="item">\n'
                html += f'<h3>{exp["position"]}</h3>\n'
                html += f'<p class="company">{exp["company"]}</p>\n'
                html += f'<p class="date-range">{exp["start_date"]} - {exp["end_date"]}</p>\n'
                html += f'<p>{exp["description"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Education
        if data['education']:
            html += '<div class="section">\n'
            html += '<h2>Education</h2>\n'
            for edu in data['education']:
                html += '<div class="item">\n'
                html += f'<h3>{edu["degree"]} in {edu["field"]}</h3>\n'
                html += f'<p class="institution">{edu["institution"]}</p>\n'
                html += f'<p class="date-range">{edu["start_date"]} - {edu["end_date"]}</p>\n'
                if edu['grade']:
                    html += f'<p>Grade: {edu["grade"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Skills
        if data['profile'] and data['profile']['skills']:
            html += '<div class="section">\n'
            html += '<h2>Skills</h2>\n'
            html += '<ul class="skills-list">\n'
            for skill in data['profile']['skills']:
                html += f'<li>{skill}</li>\n'
            html += '</ul>\n'
            html += '</div>\n\n'
        
        # Projects
        if data['projects']:
            html += '<div class="section">\n'
            html += '<h2>Projects</h2>\n'
            for proj in data['projects']:
                html += '<div class="item">\n'
                html += f'<h3>{proj["title"]}</h3>\n'
                if proj['technologies']:
                    html += f'<p>Technologies: {", ".join(proj["technologies"])}</p>\n'
                html += f'<p>{proj["description"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        return html
    
    def _generate_classic_html(self, data):
        """Generate Classic template HTML"""
        html = '<div class="header">\n'
        html += f'<h1>{data["name"] if data["name"] else "Your Name"}</h1>\n'
        
        # Contact info - centered for classic
        contact = []
        if data['email']:
            contact.append(data["email"])
        if data['phone']:
            contact.append(data["phone"])
        if data['profile'] and data['profile']['location']:
            contact.append(data["profile"]["location"])
        
        if contact:
            html += f'<div class="contact-info">{" | ".join(contact)}</div>\n'
        html += '</div>\n\n'
        
        # Career Objective
        if data['profile'] and data['profile']['career_objective']:
            html += '<div class="section">\n'
            html += '<h2>Career Objective</h2>\n'
            html += f'<p>{data["profile"]["career_objective"]}</p>\n'
            html += '</div>\n\n'
        
        # Professional Summary
        if data['profile'] and data['profile']['summary']:
            html += '<div class="section">\n'
            html += '<h2>Professional Summary</h2>\n'
            html += f'<p>{data["profile"]["summary"]}</p>\n'
            html += '</div>\n\n'
        
        # Experience
        if data['experience']:
            html += '<div class="section">\n'
            html += '<h2>Work Experience</h2>\n'
            for exp in data['experience']:
                html += '<div class="item">\n'
                html += f'<h3>{exp["position"]}</h3>\n'
                html += f'<p class="company">{exp["company"]}</p>\n'
                html += f'<p class="date-range">{exp["start_date"]} - {exp["end_date"]}</p>\n'
                html += f'<p>{exp["description"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Education
        if data['education']:
            html += '<div class="section">\n'
            html += '<h2>Education</h2>\n'
            for edu in data['education']:
                html += '<div class="item">\n'
                html += f'<h3>{edu["degree"]} in {edu["field"]}</h3>\n'
                html += f'<p class="institution">{edu["institution"]}</p>\n'
                html += f'<p class="date-range">{edu["start_date"]} - {edu["end_date"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Skills
        if data['profile'] and data['profile']['skills']:
            html += '<div class="section">\n'
            html += '<h2>Skills</h2>\n'
            html += '<ul class="skills-list">\n'
            for skill in data['profile']['skills']:
                html += f'<li>{skill}</li>\n'
            html += '</ul>\n'
            html += '</div>\n\n'
        
        return html
    
    def _generate_creative_html(self, data):
        """Generate Creative template HTML"""
        # Creative has colored header
        html = '<div class="header">\n'
        html += f'<h1>{data["name"] if data["name"] else "Your Name"}</h1>\n'
        
        # Contact info
        contact = []
        if data['email']:
            contact.append(data["email"])
        if data['phone']:
            contact.append(data["phone"])
        if data['profile'] and data['profile']['location']:
            contact.append(data["profile"]["location"])
        
        if contact:
            html += f'<div class="contact-info">{" | ".join(contact)}</div>\n'
        html += '</div>\n\n'
        
        # Professional Summary
        if data['profile'] and data['profile']['summary']:
            html += '<div class="section">\n'
            html += '<h2>About Me</h2>\n'
            html += f'<p>{data["profile"]["summary"]}</p>\n'
            html += '</div>\n\n'
        
        # Experience
        if data['experience']:
            html += '<div class="section">\n'
            html += '<h2>Experience</h2>\n'
            for exp in data['experience']:
                html += '<div class="item">\n'
                html += f'<h3>{exp["position"]}</h3>\n'
                html += f'<p class="company">{exp["company"]}</p>\n'
                html += f'<p class="date-range">{exp["start_date"]} - {exp["end_date"]}</p>\n'
                html += f'<p>{exp["description"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Education
        if data['education']:
            html += '<div class="section">\n'
            html += '<h2>Education</h2>\n'
            for edu in data['education']:
                html += '<div class="item">\n'
                html += f'<h3>{edu["degree"]} in {edu["field"]}</h3>\n'
                html += f'<p class="institution">{edu["institution"]}</p>\n'
                html += f'<p class="date-range">{edu["start_date"]} - {edu["end_date"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Skills
        if data['profile'] and data['profile']['skills']:
            html += '<div class="section">\n'
            html += '<h2>Skills</h2>\n'
            html += '<ul class="skills-list">\n'
            for skill in data['profile']['skills']:
                html += f'<li>{skill}</li>\n'
            html += '</ul>\n'
            html += '</div>\n\n'
        
        return html
    
    def _generate_minimal_html(self, data):
        """Generate Minimal template HTML"""
        html = '<div class="header">\n'
        html += f'<h1>{data["name"] if data["name"] else "Your Name"}</h1>\n'
        
        if data['profile'] and data['profile']['location']:
            html += f'<p>{data["profile"]["location"]}</p>\n'
        
        # Contact info
        contact = []
        if data['email']:
            contact.append(data["email"])
        if data['phone']:
            contact.append(data["phone"])
        
        if contact:
            html += f'<div class="contact-info">{" · ".join(contact)}</div>\n'
        html += '</div>\n\n'
        
        # Summary
        if data['profile'] and data['profile']['summary']:
            html += '<div class="section">\n'
            html += '<h2>Summary</h2>\n'
            html += f'<p>{data["profile"]["summary"]}</p>\n'
            html += '</div>\n\n'
        
        # Experience
        if data['experience']:
            html += '<div class="section">\n'
            html += '<h2>Experience</h2>\n'
            for exp in data['experience']:
                html += '<div class="item">\n'
                html += f'<h3>{exp["position"]}</h3>\n'
                html += f'<p class="company">{exp["company"]}</p>\n'
                html += f'<p class="date-range">{exp["start_date"]} - {exp["end_date"]}</p>\n'
                html += f'<p>{exp["description"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Education
        if data['education']:
            html += '<div class="section">\n'
            html += '<h2>Education</h2>\n'
            for edu in data['education']:
                html += '<div class="item">\n'
                html += f'<h3>{edu["degree"]} in {edu["field"]}</h3>\n'
                html += f'<p class="institution">{edu["institution"]}</p>\n'
                html += f'<p class="date-range">{edu["start_date"]} - {edu["end_date"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Skills
        if data['profile'] and data['profile']['skills']:
            html += '<div class="section">\n'
            html += '<h2>Skills</h2>\n'
            html += '<ul class="skills-list">\n'
            for skill in data['profile']['skills']:
                html += f'<li>{skill}</li>\n'
            html += '</ul>\n'
            html += '</div>\n\n'
        
        return html
    
    def _generate_executive_html(self, data):
        """Generate Executive template HTML"""
        html = '<div class="header">\n'
        html += f'<h1>{data["name"] if data["name"] else "Your Name"}</h1>\n'
        
        # Contact info - centered
        contact = []
        if data['email']:
            contact.append(data["email"])
        if data['phone']:
            contact.append(data["phone"])
        if data['profile'] and data['profile']['location']:
            contact.append(data["profile"]["location"])
        
        if contact:
            html += f'<div class="contact-info">{" | ".join(contact)}</div>\n'
        html += '</div>\n\n'
        
        # Executive Summary
        if data['profile'] and data['profile']['summary']:
            html += '<div class="section">\n'
            html += '<h2>Executive Summary</h2>\n'
            html += f'<p>{data["profile"]["summary"]}</p>\n'
            html += '</div>\n\n'
        
        # Professional Experience
        if data['experience']:
            html += '<div class="section">\n'
            html += '<h2>Professional Experience</h2>\n'
            for exp in data['experience']:
                html += '<div class="item">\n'
                html += f'<h3>{exp["position"]}</h3>\n'
                html += f'<p class="company">{exp["company"]}</p>\n'
                html += f'<p class="date-range">{exp["start_date"]} - {exp["end_date"]}</p>\n'
                html += f'<p>{exp["description"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Education
        if data['education']:
            html += '<div class="section">\n'
            html += '<h2>Education</h2>\n'
            for edu in data['education']:
                html += '<div class="item">\n'
                html += f'<h3>{edu["degree"]} in {edu["field"]}</h3>\n'
                html += f'<p class="institution">{edu["institution"]}</p>\n'
                html += f'<p class="date-range">{edu["start_date"]} - {edu["end_date"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Core Competencies
        if data['profile'] and data['profile']['skills']:
            html += '<div class="section">\n'
            html += '<h2>Core Competencies</h2>\n'
            html += '<ul class="skills-list">\n'
            for skill in data['profile']['skills']:
                html += f'<li>{skill}</li>\n'
            html += '</ul>\n'
            html += '</div>\n\n'
        
        return html
    
    def _generate_technical_html(self, data):
        """Generate Technical template HTML"""
        # Technical has dark header
        html = '<div class="header">\n'
        html += f'<h1>&lt;{data["name"] if data["name"] else "Your Name"} /&gt;</h1>\n'
        
        # Contact info in header
        contact = []
        if data['email']:
            contact.append(data["email"])
        if data['phone']:
            contact.append(data["phone"])
        if data['profile'] and data['profile']['location']:
            contact.append(data["profile"]["location"])
        
        if contact:
            html += f'<div class="contact-info">{" | ".join(contact)}</div>\n'
        html += '</div>\n\n'
        
        # Technical Summary
        if data['profile'] and data['profile']['summary']:
            html += '<div class="section">\n'
            html += '<h2>// Technical Summary</h2>\n'
            html += f'<p>{data["profile"]["summary"]}</p>\n'
            html += '</div>\n\n'
        
        # Technical Skills
        if data['profile'] and data['profile']['skills']:
            html += '<div class="section">\n'
            html += '<h2>// Technical Skills</h2>\n'
            html += '<ul class="skills-list">\n'
            for skill in data['profile']['skills']:
                html += f'<li>{skill}</li>\n'
            html += '</ul>\n'
            html += '</div>\n\n'
        
        # Experience
        if data['experience']:
            html += '<div class="section">\n'
            html += '<h2>// Work Experience</h2>\n'
            for exp in data['experience']:
                html += '<div class="item">\n'
                html += f'<h3>{exp["position"]}</h3>\n'
                html += f'<p class="company">{exp["company"]}</p>\n'
                html += f'<p class="date-range">{exp["start_date"]} - {exp["end_date"]}</p>\n'
                html += f'<p>{exp["description"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Projects
        if data['projects']:
            html += '<div class="section">\n'
            html += '<h2>// Projects</h2>\n'
            for proj in data['projects']:
                html += '<div class="item">\n'
                html += f'<h3>{proj["title"]}</h3>\n'
                if proj['technologies']:
                    html += f'<p>Tech Stack: {", ".join(proj["technologies"])}</p>\n'
                html += f'<p>{proj["description"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        # Education
        if data['education']:
            html += '<div class="section">\n'
            html += '<h2>// Education</h2>\n'
            for edu in data['education']:
                html += '<div class="item">\n'
                html += f'<h3>{edu["degree"]} in {edu["field"]}</h3>\n'
                html += f'<p class="institution">{edu["institution"]}</p>\n'
                html += f'<p class="date-range">{edu["start_date"]} - {edu["end_date"]}</p>\n'
                html += '</div>\n'
            html += '</div>\n\n'
        
        return html

    
    def _generate_fallback_cover_letter(self, data=None):
        """
        Generate a basic cover letter without AI when API key is not available.
        """
        if data is None:
            data = self._gather_user_data()
        
        content = f"{data.get('name', 'Your Name')}\n"
        content += f"{data.get('email', 'your.email@example.com')}\n\n"
        
        content += "Dear Hiring Manager,\n\n"
        
        position = data.get('position', '')
        company = data.get('company_name', '')
        
        if position and company:
            content += f"I am writing to express my strong interest in the {position} position at {company}.\n\n"
        else:
            content += "I am writing to express my interest in opportunities with your organization.\n\n"
        
        profile = data.get('profile', {})
        if profile and profile.get('summary'):
            content += f"{profile['summary']}\n\n"
        
        experience = data.get('experience', [])
        if experience:
            exp = experience[0]
            content += f"In my recent role as {exp.get('position', 'a professional')} at {exp.get('company', 'my previous company')}, I have gained valuable experience that aligns well with your requirements.\n\n"
        
        content += "I am excited about the opportunity to contribute to your team and would welcome the chance to discuss how my skills and experience can benefit your organization.\n\n"
        content += "Thank you for considering my application. I look forward to hearing from you.\n\n"
        content += f"Sincerely,\n{data.get('name', 'Your Name')}"
        
        return content
