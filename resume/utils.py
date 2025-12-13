"""
Utility functions for PDF generation and other helper functions.
"""
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False
    HTML = None
    CSS = None
    FontConfiguration = None

# Try to import ReportLab as fallback
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def get_template_css(template='modern'):
    """
    Get CSS styling based on template choice.
    
    Args:
        template: Template ID (modern, classic, creative, minimal, executive, technical)
    
    Returns:
        CSS string for the template
    """
    
    # Base CSS that applies to all templates
    base_css = '''
        @page {
            size: A4;
            margin: 2cm;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            line-height: 1.6;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        h1 {
            margin-top: 0;
            margin-bottom: 10px;
            line-height: 1.2;
        }
        h2 {
            margin-top: 15px;
            margin-bottom: 8px;
            line-height: 1.3;
        }
        h3 {
            margin-top: 10px;
            margin-bottom: 5px;
            line-height: 1.3;
        }
        h4, h5, h6 {
            margin-top: 8px;
            margin-bottom: 5px;
            line-height: 1.3;
        }
        p {
            margin: 8px 0;
            line-height: 1.6;
        }
        ul {
            margin: 8px 0;
            padding-left: 25px;
        }
        li {
            margin: 4px 0;
            line-height: 1.5;
        }
        hr {
            margin: 15px 0;
            border: none;
            border-top: 1px solid #ccc;
        }
        strong {
            font-weight: 600;
        }
        .section {
            margin-bottom: 20px;
            page-break-inside: avoid;
        }
        .contact-info {
            margin-bottom: 15px;
        }
        .contact-info p {
            margin: 3px 0;
        }
        .date-range {
            color: #666;
            font-size: 10pt;
            font-style: italic;
        }
        .item {
            margin-bottom: 15px;
            page-break-inside: avoid;
        }
        .item h3 {
            margin-bottom: 3px;
        }
        .item p {
            margin: 3px 0;
        }
        .company, .institution {
            color: #666;
            font-size: 10pt;
        }
        .skills-list {
            list-style: none;
            padding-left: 0;
        }
        .skills-list li {
            display: inline-block;
            background: #f0f0f0;
            padding: 4px 10px;
            margin: 3px;
            border-radius: 3px;
            font-size: 10pt;
        }
        .header {
            margin-bottom: 20px;
            page-break-after: avoid;
        }
        .content {
            line-height: 1.8;
        }
    '''
    
    # Template-specific CSS
    template_styles = {
        'modern': '''
            body {
                font-family: 'Arial', sans-serif;
                font-size: 10pt;
                color: #212529;
                background: white;
            }
            .header {
                border-left: 8px solid #0d6efd;
                padding-left: 15px;
                margin-bottom: 20px;
            }
            h1 {
                font-size: 24pt;
                color: #0d6efd;
                margin: 0;
                font-weight: bold;
            }
            h1 + p {
                font-size: 12pt;
                color: #495057;
                margin: 5px 0;
                font-weight: 600;
            }
            .contact-info {
                font-size: 9pt;
                color: #212529;
                margin: 8px 0;
                font-weight: 500;
            }
            h2 {
                font-size: 13pt;
                color: #0d6efd;
                margin-top: 20px;
                margin-bottom: 10px;
                border-bottom: 3px solid #0d6efd;
                padding-bottom: 5px;
                font-weight: bold;
                text-transform: uppercase;
            }
            h3 {
                font-size: 11pt;
                color: #212529;
                margin: 0 0 5px 0;
                font-weight: bold;
            }
            .section {
                margin-bottom: 20px;
            }
            .item {
                margin-bottom: 15px;
            }
            .company, .institution {
                color: #495057;
                font-size: 9pt;
                margin: 3px 0;
            }
            .date-range {
                color: #495057;
                font-size: 9pt;
                font-weight: 600;
                float: right;
            }
            ul {
                margin: 8px 0;
                padding-left: 20px;
                color: #212529;
                font-size: 9pt;
                line-height: 1.7;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
            }
            .skills-list li {
                display: inline-block;
                background: #0d6efd;
                color: white;
                padding: 5px 12px;
                margin: 3px;
                border-radius: 15px;
                font-size: 9pt;
                font-weight: 600;
            }
        ''',
        
        'classic': '''
            body {
                font-family: Georgia, 'Times New Roman', serif;
                font-size: 10pt;
                color: #2c3e50;
                background: white;
            }
            h1 {
                font-size: 22pt;
                color: #2c3e50;
                text-align: center;
                margin: 0 0 5px 0;
                letter-spacing: 2px;
                border-bottom: 3px double #2c3e50;
                padding-bottom: 10px;
                font-weight: bold;
            }
            .contact-info {
                font-size: 9pt;
                color: #7f8c8d;
                text-align: center;
                margin: 8px 0 20px 0;
            }
            h2 {
                font-size: 12pt;
                color: #2c3e50;
                margin-top: 20px;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-bottom: 2px solid #2c3e50;
                padding-bottom: 5px;
                font-weight: bold;
            }
            h3 {
                font-size: 11pt;
                color: #2c3e50;
                margin: 0 0 5px 0;
                font-weight: bold;
            }
            .section {
                margin-bottom: 20px;
            }
            .item {
                margin-bottom: 15px;
            }
            .company, .institution {
                color: #7f8c8d;
                font-size: 9pt;
                font-style: italic;
                margin: 3px 0;
            }
            .date-range {
                color: #7f8c8d;
                font-size: 9pt;
                float: right;
            }
            ul {
                margin: 8px 0;
                padding-left: 20px;
                font-size: 9pt;
                line-height: 1.7;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
            }
            .skills-list li {
                display: inline-block;
                background: #f0f0f0;
                color: #2c3e50;
                padding: 5px 12px;
                margin: 3px;
                border-radius: 5px;
                font-size: 9pt;
                border: 1px solid #2c3e50;
            }
        ''',
        
        'creative': '''
            body {
                font-family: 'Arial', sans-serif;
                font-size: 9pt;
                color: #2c3e50;
                background: white;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                margin: -2cm -2cm 20px -2cm;
            }
            h1 {
                font-size: 28pt;
                color: white;
                margin: 0 0 5px 0;
                font-weight: bold;
            }
            h1 + p {
                font-size: 12pt;
                color: white;
                margin: 5px 0;
                font-weight: 600;
            }
            .contact-info {
                font-size: 8pt;
                color: white;
                margin: 8px 0;
            }
            h2 {
                font-size: 13pt;
                color: #667eea;
                margin-top: 20px;
                margin-bottom: 10px;
                border-bottom: 3px solid #667eea;
                padding-bottom: 5px;
                font-weight: bold;
                text-transform: uppercase;
            }
            h3 {
                font-size: 11pt;
                color: #2c3e50;
                margin: 0 0 5px 0;
                font-weight: bold;
            }
            .section {
                margin-bottom: 20px;
                padding-left: 15px;
                border-left: 3px solid #667eea;
            }
            .item {
                margin-bottom: 15px;
            }
            .company, .institution {
                color: #667eea;
                font-size: 9pt;
                font-weight: bold;
                margin: 3px 0;
            }
            .date-range {
                color: #7f8c8d;
                font-size: 8pt;
            }
            ul {
                margin: 8px 0;
                padding-left: 20px;
                font-size: 9pt;
                line-height: 1.6;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
            }
            .skills-list li {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 5px 12px;
                margin: 3px;
                border-radius: 15px;
                font-size: 8pt;
                font-weight: 600;
            }
        ''',
        
        'minimal': '''
            body {
                font-family: 'Helvetica', 'Arial', sans-serif;
                font-size: 10pt;
                color: #1a1a1a;
                background: white;
            }
            h1 {
                font-size: 32pt;
                color: #1a1a1a;
                margin: 0 0 5px 0;
                font-weight: 300;
                letter-spacing: -1px;
            }
            h1 + p {
                font-size: 11pt;
                color: #999;
                margin: 5px 0;
                font-weight: 400;
            }
            .contact-info {
                font-size: 9pt;
                color: #999;
                margin: 8px 0 20px 0;
            }
            h2 {
                font-size: 11pt;
                color: #1a1a1a;
                margin-top: 25px;
                margin-bottom: 15px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            h3 {
                font-size: 11pt;
                color: #1a1a1a;
                margin: 0 0 5px 0;
                font-weight: 600;
            }
            .section {
                margin-bottom: 20px;
            }
            .item {
                margin-bottom: 15px;
            }
            .company, .institution {
                color: #666;
                font-size: 9pt;
                margin: 3px 0;
            }
            .date-range {
                color: #999;
                font-size: 8pt;
                float: right;
            }
            ul {
                margin: 8px 0;
                padding-left: 20px;
                font-size: 9pt;
                line-height: 1.7;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
            }
            .skills-list li {
                display: inline-block;
                background: #1a1a1a;
                color: white;
                padding: 5px 12px;
                margin: 3px;
                border-radius: 0;
                font-size: 8pt;
                font-weight: 400;
            }
        ''',
        
        'executive': '''
            body {
                font-family: 'Times New Roman', serif;
                font-size: 10pt;
                color: #1a1a1a;
                background: white;
            }
            h1 {
                font-size: 28pt;
                color: #1a1a1a;
                text-align: center;
                margin: 0 0 8px 0;
                font-weight: bold;
                letter-spacing: 3px;
                border-bottom: 4px solid #1a1a1a;
                padding-bottom: 12px;
            }
            .contact-info {
                font-size: 9pt;
                color: #666;
                text-align: center;
                margin: 8px 0 20px 0;
            }
            h2 {
                font-size: 13pt;
                color: #1a1a1a;
                margin-top: 20px;
                margin-bottom: 10px;
                font-weight: bold;
                border-bottom: 2px solid #1a1a1a;
                padding-bottom: 5px;
                text-transform: uppercase;
            }
            h3 {
                font-size: 11pt;
                color: #1a1a1a;
                margin: 0 0 5px 0;
                font-weight: bold;
            }
            .section {
                margin-bottom: 20px;
            }
            .item {
                margin-bottom: 15px;
            }
            .company, .institution {
                color: #444;
                font-size: 10pt;
                font-style: italic;
                margin: 3px 0;
            }
            .date-range {
                color: #666;
                font-size: 9pt;
                float: right;
                font-weight: bold;
            }
            ul {
                margin: 8px 0;
                padding-left: 20px;
                font-size: 9pt;
                line-height: 1.7;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
            }
            .skills-list li {
                display: inline-block;
                background: #f0f0f0;
                color: #1a1a1a;
                padding: 5px 12px;
                margin: 3px;
                border-radius: 5px;
                font-size: 9pt;
                font-weight: bold;
                border: 2px solid #1a1a1a;
            }
        ''',
        
        'technical': '''
            body {
                font-family: 'Courier New', 'Consolas', monospace;
                font-size: 9pt;
                color: #2c3e50;
                background: white;
            }
            .header {
                background-color: #1a1a1a;
                color: #ffffff;
                padding: 15px;
                margin: -2cm -2cm 20px -2cm;
            }
            h1 {
                font-size: 22pt;
                color: #00d4ff;
                margin: 0;
                font-weight: bold;
            }
            h1 + p {
                font-size: 10pt;
                color: #ffffff;
                margin: 5px 0;
            }
            .contact-info {
                font-size: 8pt;
                color: #00d4ff;
                margin: 8px 0;
            }
            h2 {
                font-size: 12pt;
                color: #00d4ff;
                margin-top: 20px;
                margin-bottom: 10px;
                font-family: Arial, sans-serif;
                font-weight: bold;
                text-transform: uppercase;
            }
            h3 {
                font-size: 10pt;
                color: #2c3e50;
                margin: 0 0 5px 0;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }
            .section {
                margin-bottom: 20px;
                background-color: #f8f9fa;
                padding: 10px;
                border-left: 4px solid #00d4ff;
                font-family: Arial, sans-serif;
            }
            .item {
                margin-bottom: 15px;
            }
            .company, .institution {
                color: #495057;
                font-size: 8pt;
                font-family: Arial, sans-serif;
                margin: 3px 0;
            }
            .date-range {
                color: #6c757d;
                font-size: 8pt;
                font-family: Arial, sans-serif;
            }
            ul {
                margin: 8px 0;
                padding-left: 20px;
                font-size: 8pt;
                line-height: 1.6;
                font-family: Arial, sans-serif;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
            }
            .skills-list li {
                display: inline-block;
                background: #1a1a1a;
                color: #00d4ff;
                padding: 5px 12px;
                margin: 3px;
                border-radius: 0;
                font-size: 8pt;
                border: 1px solid #00d4ff;
                font-family: 'Courier New', monospace;
            }
        '''
    }
    
    # Get template-specific CSS or default to modern
    specific_css = template_styles.get(template, template_styles['modern'])
    
    return base_css + specific_css


def generate_pdf_from_html(html_content, filename='resume.pdf', template='modern'):
    """
    Generate a PDF file from HTML content using WeasyPrint (preferred) or ReportLab (fallback).
    
    Args:
        html_content: HTML string to convert to PDF
        filename: Name of the PDF file
        template: Template ID for styling
    
    Returns:
        HttpResponse with PDF content
    """
    if WEASYPRINT_AVAILABLE:
        # Use WeasyPrint if available
        buffer = BytesIO()
        
        # Font configuration for better rendering (if available)
        font_config = FontConfiguration() if FontConfiguration else None
        
        # Get template-specific CSS
        css_string = get_template_css(template)
        css = CSS(string=css_string, font_config=font_config) if CSS else None
        
        # Generate PDF
        if HTML:
            HTML(string=html_content).write_pdf(buffer, stylesheets=[css] if css else [], font_config=font_config)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Create HTTP response
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    elif REPORTLAB_AVAILABLE:
        # Use ReportLab as fallback
        return generate_pdf_with_reportlab(html_content, filename, template)
    
    else:
        # Neither library available
        response = HttpResponse("PDF generation is currently unavailable. Please install WeasyPrint or ReportLab.", 
                              content_type='text/plain')
        response.status_code = 503  # Service Unavailable
        return response


def generate_pdf_with_reportlab(html_content, filename='resume.pdf', template='modern'):
    """
    Generate a PDF file from HTML content using ReportLab as fallback.
    
    Args:
        html_content: HTML string to convert to PDF
        filename: Name of the PDF file
        template: Template ID for styling
    
    Returns:
        HttpResponse with PDF content
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
    )
    
    # Parse HTML content (basic parsing)
    story = []
    
    # Simple HTML to text conversion (basic implementation)
    import re
    from html import unescape
    
    # Remove HTML tags and convert to plain text
    text_content = re.sub(r'<[^>]+>', '', html_content)
    text_content = unescape(text_content)
    
    # Split into paragraphs
    paragraphs = text_content.split('\n\n')
    
    for para in paragraphs:
        para = para.strip()
        if para:
            if len(para) < 50 and not para.endswith('.'):
                # Likely a title
                story.append(Paragraph(para, title_style))
            else:
                # Regular paragraph
                story.append(Paragraph(para, normal_style))
            story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Create HTTP response
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def format_resume_for_pdf(user, resume_content):
    """
    Format resume content into HTML suitable for PDF generation.
    
    Args:
        user: User object
        resume_content: Resume text content (can be HTML or markdown)
    
    Returns:
        Formatted HTML string
    """
    import re
    from html import escape
    
    # Check if content is already HTML (starts with HTML tags)
    if resume_content.strip().startswith('<'):
        # Content is already HTML from our template generators
        # Wrap it in a basic HTML structure for PDF rendering
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Resume</title>
</head>
<body>
{resume_content}
</body>
</html>
        '''
        return html
    
    # Legacy markdown format - escape and convert
    content = escape(resume_content)
    
    # Process the content line by line for better formatting
    lines = content.split('\n')
    formatted_lines = []
    in_list = False
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # Empty line - close any open paragraph or list
            if current_paragraph:
                formatted_lines.append(f"<p>{'<br>'.join(current_paragraph)}</p>")
                current_paragraph = []
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            continue
        
        # Check for headers
        if line.startswith('# '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            if current_paragraph:
                formatted_lines.append(f"<p>{'<br>'.join(current_paragraph)}</p>")
                current_paragraph = []
            formatted_lines.append(f"<h1>{line[2:].strip()}</h1>")
        elif line.startswith('## '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            if current_paragraph:
                formatted_lines.append(f"<p>{'<br>'.join(current_paragraph)}</p>")
                current_paragraph = []
            formatted_lines.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith('### '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            if current_paragraph:
                formatted_lines.append(f"<p>{'<br>'.join(current_paragraph)}</p>")
                current_paragraph = []
            formatted_lines.append(f"<h3>{line[4:].strip()}</h3>")
        # Check for list items
        elif line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
            if current_paragraph:
                formatted_lines.append(f"<p>{'<br>'.join(current_paragraph)}</p>")
                current_paragraph = []
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            item_text = line[2:].strip() if line.startswith(('- ', '* ')) else line[2:].strip()
            # Handle bold text in list items
            item_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item_text)
            formatted_lines.append(f"<li>{item_text}</li>")
        # Check for horizontal rules
        elif line in ['---', '***', '___']:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            if current_paragraph:
                formatted_lines.append(f"<p>{'<br>'.join(current_paragraph)}</p>")
                current_paragraph = []
            formatted_lines.append('<hr>')
        # Regular text line
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            # Handle bold text
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            current_paragraph.append(line)
    
    # Close any remaining open elements
    if current_paragraph:
        formatted_lines.append(f"<p>{'<br>'.join(current_paragraph)}</p>")
    if in_list:
        formatted_lines.append('</ul>')
    
    # Build final HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Resume - {escape(user.get_full_name())}</title>
    </head>
    <body>
        {''.join(formatted_lines)}
    </body>
    </html>
    """
    
    return html_content


def markdown_to_html(text):
    """
    Convert simple markdown formatting to HTML.
    Supports headers, bold, lists, and line breaks.
    """
    import re
    
    # Replace headers
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    # Replace bold text
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    # Replace horizontal rules
    text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)
    
    # Replace line breaks with paragraphs
    paragraphs = text.split('\n\n')
    html_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para:
            # Check if it's a list
            if para.startswith('- ') or para.startswith('* '):
                items = para.split('\n')
                list_html = '<ul>'
                for item in items:
                    item = item.lstrip('- ').lstrip('* ').strip()
                    if item:
                        list_html += f'<li>{item}</li>'
                list_html += '</ul>'
                html_paragraphs.append(list_html)
            # Check if it's already an HTML tag
            elif para.startswith('<'):
                html_paragraphs.append(para)
            else:
                # Regular paragraph
                html_paragraphs.append(f'<p>{para}</p>')
    
    return '\n'.join(html_paragraphs)


def create_portfolio_html(user):
    """
    Create a complete portfolio HTML page for a user.
    
    Args:
        user: User object
    
    Returns:
        HTML string
    """
    from .models import Profile, Education, Experience, Project
    from html import escape
    
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None
    
    educations = Education.objects.filter(user=user).order_by('-start_date')
    experiences = Experience.objects.filter(user=user).order_by('-start_date')
    projects = Project.objects.filter(user=user)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Portfolio - {escape(user.get_full_name())}</title>
    </head>
    <body>
        <div class="header">
            <h1>{escape(user.get_full_name())}</h1>
            <div class="contact-info">
                <p>{escape(user.email)}{' | ' + escape(user.phone) if user.phone else ''}</p>
    """
    
    if profile:
        if profile.location:
            html += f"<p>{escape(profile.location)}</p>"
        if profile.linkedin_url or profile.github_url or profile.portfolio_url:
            html += "<p>"
            links = []
            if profile.linkedin_url:
                links.append(f"LinkedIn: {escape(profile.linkedin_url)}")
            if profile.github_url:
                links.append(f"GitHub: {escape(profile.github_url)}")
            if profile.portfolio_url:
                links.append(f"Website: {escape(profile.portfolio_url)}")
            html += " | ".join(links)
            html += "</p>"
    
    html += "</div></div>"
    
    if profile and profile.summary:
        html += f"""
        <div class="section">
            <h2>About Me</h2>
            <p>{escape(profile.summary)}</p>
        </div>
        """
    
    if profile and profile.skills:
        skills = profile.get_skills_list()
        html += """
        <div class="section">
            <h2>Skills</h2>
            <ul class="skills-list">
        """
        for skill in skills:
            html += f'<li>{escape(skill)}</li>'
        html += "</ul></div>"
    
    if experiences:
        html += """
        <div class="section">
            <h2>Experience</h2>
        """
        for exp in experiences:
            end_date = exp.end_date.strftime('%B %Y') if exp.end_date and not exp.currently_working else 'Present'
            html += f"""
            <div class="item">
                <h3>{escape(exp.position)}</h3>
                <p class="company">{escape(exp.company)} | {escape(exp.location)}</p>
                <p class="date-range">{exp.start_date.strftime('%B %Y')} - {end_date}</p>
                <p>{escape(exp.description)}</p>
            </div>
            """
        html += "</div>"
    
    if educations:
        html += """
        <div class="section">
            <h2>Education</h2>
        """
        for edu in educations:
            end_date = edu.end_date.strftime('%B %Y') if edu.end_date and not edu.currently_studying else 'Present'
            html += f"""
            <div class="item">
                <h3>{escape(edu.get_degree_display())} in {escape(edu.field_of_study)}</h3>
                <p class="institution">{escape(edu.institution)}</p>
                <p class="date-range">{edu.start_date.strftime('%B %Y')} - {end_date}</p>
            """
            if edu.grade:
                html += f"<p><strong>Grade:</strong> {escape(edu.grade)}</p>"
            if edu.description:
                html += f"<p>{escape(edu.description)}</p>"
            html += "</div>"
        html += "</div>"
    
    if projects:
        html += """
        <div class="section">
            <h2>Projects</h2>
        """
        for proj in projects:
            html += f"""
            <div class="item">
                <h3>{escape(proj.title)}</h3>
            """
            if proj.get_technologies_list():
                html += f"<p><strong>Technologies:</strong> {escape(', '.join(proj.get_technologies_list()))}</p>"
            html += f"<p>{escape(proj.description)}</p>"
            if proj.project_url:
                html += f'<p><strong>URL:</strong> {escape(proj.project_url)}</p>'
            html += "</div>"
        html += "</div>"
    
    html += """
    </body>
    </html>
    """
    
    return html
