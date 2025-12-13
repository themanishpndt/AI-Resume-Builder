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
    
    # Template-specific CSS with advanced designs
    template_styles = {
        'modern': '''
            @page {
                size: A4;
                margin: 2cm;
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 8pt;
                    color: #6c757d;
                }
            }
            body {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 10pt;
                color: #212529;
                background: white;
                line-height: 1.6;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px 20px;
                margin: -2cm -2cm 25px -2cm;
                border-radius: 0 0 15px 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            h1 {
                font-size: 28pt;
                color: white;
                margin: 0 0 8px 0;
                font-weight: 700;
                letter-spacing: -0.5px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            h1 + p {
                font-size: 13pt;
                color: rgba(255,255,255,0.9);
                margin: 5px 0;
                font-weight: 500;
            }
            .contact-info {
                font-size: 9pt;
                color: rgba(255,255,255,0.8);
                margin: 10px 0;
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
            }
            .contact-info p {
                margin: 0;
                display: flex;
                align-items: center;
            }
            .contact-info p:before {
                content: "•";
                margin-right: 8px;
                color: rgba(255,255,255,0.6);
            }
            h2 {
                font-size: 14pt;
                color: #667eea;
                margin-top: 25px;
                margin-bottom: 12px;
                border-bottom: 3px solid #667eea;
                padding-bottom: 8px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            h3 {
                font-size: 12pt;
                color: #212529;
                margin: 0 0 6px 0;
                font-weight: 600;
                border-left: 4px solid #667eea;
                padding-left: 10px;
            }
            .section {
                margin-bottom: 25px;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .item {
                margin-bottom: 18px;
                padding: 12px;
                background: white;
                border-radius: 6px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                border: 1px solid #e9ecef;
            }
            .company, .institution {
                color: #667eea;
                font-size: 10pt;
                font-weight: 600;
                margin: 4px 0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .date-range {
                color: #6c757d;
                font-size: 9pt;
                font-weight: 500;
                float: right;
                background: #e9ecef;
                padding: 3px 8px;
                border-radius: 12px;
            }
            ul {
                margin: 10px 0;
                padding-left: 25px;
                color: #495057;
                font-size: 9pt;
                line-height: 1.7;
            }
            li {
                margin: 5px 0;
                position: relative;
            }
            li:before {
                content: "▸";
                color: #667eea;
                font-weight: bold;
                position: absolute;
                left: -15px;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            .skills-list li {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 9pt;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s ease;
            }
            .skills-list li:hover {
                transform: translateY(-1px);
            }
        ''',
        
        'classic': '''
            @page {
                size: A4;
                margin: 2.5cm;
                @bottom-center {
                    content: counter(page);
                    font-family: 'Times New Roman', serif;
                    font-size: 9pt;
                    color: #8b4513;
                }
            }
            body {
                font-family: 'Times New Roman', serif;
                font-size: 11pt;
                color: #2c3e50;
                background: white;
                line-height: 1.5;
            }
            .header {
                text-align: center;
                border-top: 3px solid #8b4513;
                border-bottom: 3px solid #8b4513;
                padding: 20px 0;
                margin-bottom: 25px;
                background: linear-gradient(to right, rgba(139, 69, 19, 0.05), transparent, rgba(139, 69, 19, 0.05));
            }
            h1 {
                font-size: 26pt;
                color: #8b4513;
                margin: 0 0 8px 0;
                letter-spacing: 3px;
                font-weight: bold;
                text-transform: uppercase;
                border-bottom: 2px solid #8b4513;
                padding-bottom: 8px;
            }
            h1 + p {
                font-size: 12pt;
                color: #2c3e50;
                margin: 8px 0;
                font-style: italic;
                font-weight: 500;
            }
            .contact-info {
                font-size: 10pt;
                color: #7f8c8d;
                text-align: center;
                margin: 12px 0 20px 0;
                border-top: 1px solid #ecf0f1;
                padding-top: 12px;
            }
            .contact-info p {
                margin: 3px 0;
                display: inline-block;
                margin-right: 20px;
            }
            h2 {
                font-size: 14pt;
                color: #8b4513;
                margin-top: 25px;
                margin-bottom: 12px;
                text-transform: uppercase;
                letter-spacing: 2px;
                border-bottom: 2px solid #8b4513;
                padding-bottom: 6px;
                font-weight: bold;
                position: relative;
            }
            h2:after {
                content: "";
                position: absolute;
                bottom: -2px;
                left: 0;
                width: 60px;
                height: 2px;
                background: #8b4513;
            }
            h3 {
                font-size: 12pt;
                color: #2c3e50;
                margin: 0 0 6px 0;
                font-weight: bold;
                font-style: italic;
            }
            .section {
                margin-bottom: 25px;
                padding: 15px;
                background: #fdfdfd;
                border: 1px solid #ecf0f1;
                border-radius: 5px;
            }
            .item {
                margin-bottom: 18px;
                padding: 12px;
                background: white;
                border-left: 4px solid #8b4513;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            .company, .institution {
                color: #8b4513;
                font-size: 11pt;
                font-weight: bold;
                margin: 4px 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .date-range {
                color: #7f8c8d;
                font-size: 10pt;
                float: right;
                font-style: italic;
                background: #ecf0f1;
                padding: 4px 10px;
                border-radius: 15px;
                margin-top: -2px;
            }
            ul {
                margin: 10px 0;
                padding-left: 25px;
                font-size: 10pt;
                line-height: 1.6;
                color: #34495e;
            }
            li {
                margin: 5px 0;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .skills-list li {
                display: inline-block;
                background: #8b4513;
                color: white;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 10pt;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(139, 69, 19, 0.3);
                border: 2px solid #654321;
            }
        ''',
        
        'creative': '''
            @page {
                size: A4;
                margin: 1.5cm;
                background: linear-gradient(45deg, #f8f9fa 25%, transparent 25%),
                            linear-gradient(-45deg, #f8f9fa 25%, transparent 25%),
                            linear-gradient(45deg, transparent 75%, #f8f9fa 75%),
                            linear-gradient(-45deg, transparent 75%, #f8f9fa 75%);
                background-size: 20px 20px;
                background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
            }
            body {
                font-family: 'Helvetica Neue', 'Arial', sans-serif;
                font-size: 10pt;
                color: #2c3e50;
                background: white;
                line-height: 1.6;
            }
            .header {
                background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #96ceb4 75%, #feca57 100%);
                color: white;
                padding: 30px 25px;
                margin: -1.5cm -1.5cm 25px -1.5cm;
                clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%);
                position: relative;
            }
            .header:after {
                content: "";
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 20px;
                background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #96ceb4 75%, #feca57 100%);
                clip-path: polygon(0 100%, 100% 0, 100% 100%, 0 100%);
            }
            h1 {
                font-size: 32pt;
                color: white;
                margin: 0 0 10px 0;
                font-weight: 900;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                letter-spacing: -1px;
                position: relative;
                z-index: 2;
            }
            h1 + p {
                font-size: 14pt;
                color: rgba(255,255,255,0.9);
                margin: 8px 0;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }
            .contact-info {
                font-size: 10pt;
                color: rgba(255,255,255,0.8);
                margin: 12px 0;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 8px;
            }
            .contact-info p {
                margin: 0;
                display: flex;
                align-items: center;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }
            .contact-info p:before {
                content: "✨";
                margin-right: 6px;
                font-size: 12pt;
            }
            h2 {
                font-size: 16pt;
                background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-top: 30px;
                margin-bottom: 15px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 2px;
                position: relative;
            }
            h2:before {
                content: "🎨";
                position: absolute;
                left: -25px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 18pt;
            }
            h3 {
                font-size: 13pt;
                color: #2c3e50;
                margin: 0 0 8px 0;
                font-weight: 700;
                border-bottom: 3px solid #ff6b6b;
                padding-bottom: 5px;
                display: inline-block;
            }
            .section {
                margin-bottom: 25px;
                background: linear-gradient(135deg, rgba(255, 107, 107, 0.05), rgba(78, 205, 196, 0.05));
                padding: 20px;
                border-radius: 15px;
                border: 2px solid transparent;
                background-clip: padding-box;
                position: relative;
            }
            .section:before {
                content: "";
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
                border-radius: 15px;
                z-index: -1;
            }
            .item {
                margin-bottom: 20px;
                padding: 15px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                border: 1px solid rgba(255, 107, 107, 0.2);
                position: relative;
                overflow: hidden;
            }
            .item:before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: linear-gradient(to bottom, #ff6b6b, #4ecdc4);
            }
            .company, .institution {
                color: #ff6b6b;
                font-size: 11pt;
                font-weight: 700;
                margin: 5px 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .date-range {
                color: #6c757d;
                font-size: 9pt;
                float: right;
                background: linear-gradient(135deg, #4ecdc4, #45b7d1);
                color: white;
                padding: 4px 10px;
                border-radius: 15px;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            ul {
                margin: 12px 0;
                padding-left: 25px;
                color: #495057;
                font-size: 10pt;
                line-height: 1.7;
            }
            li {
                margin: 6px 0;
                position: relative;
            }
            li:before {
                content: "🌟";
                position: absolute;
                left: -20px;
                font-size: 8pt;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .skills-list li {
                display: inline-block;
                background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%);
                color: white;
                padding: 8px 16px;
                border-radius: 25px;
                font-size: 10pt;
                font-weight: 700;
                box-shadow: 0 3px 8px rgba(0,0,0,0.15);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                position: relative;
                overflow: hidden;
            }
            .skills-list li:before {
                content: "⚡";
                margin-right: 5px;
            }
            .skills-list li:after {
                content: "";
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            .skills-list li:hover:after {
                left: 100%;
            }
        ''',
        
        'minimal': '''
            @page {
                size: A4;
                margin: 3cm;
            }
            body {
                font-family: 'Inter', 'Helvetica Neue', sans-serif;
                font-size: 11pt;
                color: #1a1a1a;
                background: white;
                line-height: 1.4;
                font-weight: 400;
            }
            .header {
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 1px solid #e5e5e5;
            }
            h1 {
                font-size: 36pt;
                color: #1a1a1a;
                margin: 0 0 8px 0;
                font-weight: 300;
                letter-spacing: -2px;
                line-height: 1.1;
            }
            h1 + p {
                font-size: 14pt;
                color: #666;
                margin: 8px 0;
                font-weight: 400;
                font-style: italic;
            }
            .contact-info {
                font-size: 10pt;
                color: #999;
                margin: 15px 0 0 0;
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }
            .contact-info p {
                margin: 0;
                font-weight: 400;
            }
            h2 {
                font-size: 13pt;
                color: #1a1a1a;
                margin-top: 35px;
                margin-bottom: 18px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 3px;
                border-top: 1px solid #e5e5e5;
                padding-top: 15px;
                position: relative;
            }
            h2:first-of-type {
                border-top: none;
                padding-top: 0;
                margin-top: 0;
            }
            h3 {
                font-size: 12pt;
                color: #1a1a1a;
                margin: 0 0 8px 0;
                font-weight: 600;
                line-height: 1.3;
            }
            .section {
                margin-bottom: 30px;
            }
            .item {
                margin-bottom: 22px;
                padding-left: 0;
                position: relative;
            }
            .item:not(:last-child):after {
                content: "";
                position: absolute;
                bottom: -11px;
                left: 0;
                width: 100%;
                height: 1px;
                background: linear-gradient(to right, #e5e5e5, transparent);
            }
            .company, .institution {
                color: #666;
                font-size: 11pt;
                font-weight: 500;
                margin: 5px 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .date-range {
                color: #999;
                font-size: 9pt;
                font-weight: 400;
                float: right;
                font-style: normal;
            }
            ul {
                margin: 12px 0;
                padding-left: 0;
                font-size: 10pt;
                line-height: 1.6;
                list-style: none;
            }
            li {
                margin: 6px 0;
                position: relative;
                padding-left: 15px;
            }
            li:before {
                content: "—";
                position: absolute;
                left: 0;
                color: #999;
                font-weight: 300;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
            }
            .skills-list li {
                display: inline-block;
                background: transparent;
                color: #1a1a1a;
                padding: 6px 0;
                border-bottom: 1px solid #1a1a1a;
                font-size: 10pt;
                font-weight: 500;
                position: relative;
            }
            .skills-list li:after {
                content: "";
                position: absolute;
                bottom: 0;
                left: 0;
                width: 0;
                height: 1px;
                background: #1a1a1a;
                transition: width 0.3s ease;
            }
            .skills-list li:hover:after {
                width: 100%;
            }
            p {
                margin: 8px 0;
                color: #333;
                font-weight: 400;
            }
            strong {
                font-weight: 600;
                color: #1a1a1a;
            }
        ''',
        
        'executive': '''
            @page {
                size: A4;
                margin: 2.5cm;
                @bottom-center {
                    content: "Confidential - " counter(page) " of " counter(pages);
                    font-family: 'Times New Roman', serif;
                    font-size: 9pt;
                    color: #2c3e50;
                    font-weight: bold;
                }
            }
            body {
                font-family: 'Times New Roman', serif;
                font-size: 11pt;
                color: #2c3e50;
                background: white;
                line-height: 1.5;
                font-weight: 400;
            }
            .header {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 35px 30px;
                margin: -2.5cm -2.5cm 30px -2.5cm;
                text-align: center;
                position: relative;
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            }
            .header:before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.03)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.03)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.02)"/><circle cx="10" cy="50" r="0.5" fill="rgba(255,255,255,0.02)"/><circle cx="90" cy="50" r="0.5" fill="rgba(255,255,255,0.02)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            }
            h1 {
                font-size: 32pt;
                color: white;
                margin: 0 0 10px 0;
                font-weight: bold;
                letter-spacing: 4px;
                text-transform: uppercase;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                position: relative;
                z-index: 2;
            }
            h1 + p {
                font-size: 14pt;
                color: rgba(255,255,255,0.9);
                margin: 10px 0;
                font-weight: 500;
                font-style: italic;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }
            .contact-info {
                font-size: 11pt;
                color: rgba(255,255,255,0.8);
                margin: 15px 0 0 0;
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 25px;
            }
            .contact-info p {
                margin: 0;
                display: flex;
                align-items: center;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }
            .contact-info p:before {
                content: "♦";
                margin-right: 8px;
                color: #f39c12;
                font-size: 8pt;
            }
            h2 {
                font-size: 15pt;
                color: #2c3e50;
                margin-top: 30px;
                margin-bottom: 15px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 2px;
                border-bottom: 3px solid #f39c12;
                padding-bottom: 8px;
                position: relative;
            }
            h2:after {
                content: "";
                position: absolute;
                bottom: -3px;
                left: 0;
                width: 80px;
                height: 3px;
                background: linear-gradient(to right, #f39c12, #e74c3c);
            }
            h3 {
                font-size: 13pt;
                color: #2c3e50;
                margin: 0 0 8px 0;
                font-weight: bold;
                font-style: italic;
                border-left: 5px solid #f39c12;
                padding-left: 12px;
            }
            .section {
                margin-bottom: 28px;
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
                box-shadow: 0 3px 10px rgba(0,0,0,0.05);
            }
            .item {
                margin-bottom: 20px;
                padding: 15px;
                background: white;
                border-radius: 6px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #ecf0f1;
                position: relative;
            }
            .item:before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 5px;
                height: 100%;
                background: linear-gradient(to bottom, #f39c12, #e74c3c);
                border-radius: 6px 0 0 6px;
            }
            .company, .institution {
                color: #2c3e50;
                font-size: 12pt;
                font-weight: bold;
                margin: 5px 0;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-style: normal;
            }
            .date-range {
                color: #7f8c8d;
                font-size: 10pt;
                float: right;
                background: #ecf0f1;
                padding: 5px 12px;
                border-radius: 20px;
                font-weight: 600;
                margin-top: -2px;
                border: 2px solid #bdc3c7;
            }
            ul {
                margin: 12px 0;
                padding-left: 25px;
                font-size: 10pt;
                line-height: 1.6;
                color: #34495e;
            }
            li {
                margin: 6px 0;
                position: relative;
            }
            li:before {
                content: "■";
                position: absolute;
                left: -15px;
                color: #f39c12;
                font-size: 6pt;
                top: 6px;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
            }
            .skills-list li {
                display: inline-block;
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 8px 16px;
                border-radius: 25px;
                font-size: 10pt;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                box-shadow: 0 3px 8px rgba(0,0,0,0.15);
                border: 2px solid #1a252f;
                position: relative;
            }
            .skills-list li:before {
                content: "★";
                margin-right: 5px;
                color: #f39c12;
            }
            p {
                margin: 10px 0;
                color: #34495e;
                font-weight: 400;
                text-align: justify;
            }
            strong {
                font-weight: bold;
                color: #2c3e50;
            }
        ''',
        
        'technical': '''
            @page {
                size: A4;
                margin: 2cm;
                background: linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px),
                            linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px);
                background-size: 20px 20px;
            }
            body {
                font-family: 'Fira Code', 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
                color: #2c3e50;
                background: white;
                line-height: 1.4;
                font-weight: 400;
            }
            .header {
                background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
                color: white;
                padding: 25px 20px;
                margin: -2cm -2cm 25px -2cm;
                position: relative;
                overflow: hidden;
            }
            .header:before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: repeating-linear-gradient(
                    45deg,
                    transparent,
                    transparent 10px,
                    rgba(0, 212, 255, 0.1) 10px,
                    rgba(0, 212, 255, 0.1) 20px
                );
            }
            h1 {
                font-size: 28pt;
                color: #00d4ff;
                margin: 0 0 8px 0;
                font-weight: bold;
                font-family: 'Fira Code', monospace;
                text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
                position: relative;
                z-index: 2;
                letter-spacing: 2px;
            }
            h1 + p {
                font-size: 12pt;
                color: rgba(255,255,255,0.9);
                margin: 8px 0;
                font-weight: 500;
                font-style: italic;
                position: relative;
                z-index: 2;
            }
            .contact-info {
                font-size: 10pt;
                color: #00d4ff;
                margin: 12px 0 0 0;
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 20px;
                position: relative;
                z-index: 2;
            }
            .contact-info p {
                margin: 0;
                display: flex;
                align-items: center;
            }
            .contact-info p:before {
                content: ">";
                margin-right: 6px;
                color: #00d4ff;
                font-weight: bold;
            }
            h2 {
                font-size: 14pt;
                color: #00d4ff;
                margin-top: 25px;
                margin-bottom: 12px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-bottom: 2px solid #00d4ff;
                padding-bottom: 6px;
                position: relative;
            }
            h2:before {
                content: "// ";
                color: #00d4ff;
                font-weight: bold;
            }
            h3 {
                font-size: 11pt;
                color: #2c3e50;
                margin: 0 0 6px 0;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                border-left: 4px solid #00d4ff;
                padding-left: 10px;
                background: rgba(0, 212, 255, 0.05);
                padding-top: 4px;
                padding-bottom: 4px;
            }
            .section {
                margin-bottom: 22px;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                border: 1px solid #e9ecef;
                border-left: 4px solid #00d4ff;
                box-shadow: 0 2px 8px rgba(0, 212, 255, 0.1);
                position: relative;
            }
            .section:before {
                content: "/*";
                position: absolute;
                top: 10px;
                right: 15px;
                color: #00d4ff;
                font-size: 12pt;
                opacity: 0.3;
            }
            .section:after {
                content: "*/";
                position: absolute;
                bottom: 10px;
                right: 15px;
                color: #00d4ff;
                font-size: 12pt;
                opacity: 0.3;
            }
            .item {
                margin-bottom: 16px;
                padding: 12px;
                background: white;
                border-radius: 4px;
                border: 1px solid #dee2e6;
                border-left: 3px solid #00d4ff;
                box-shadow: 0 1px 4px rgba(0,0,0,0.05);
                position: relative;
            }
            .company, .institution {
                color: #495057;
                font-size: 10pt;
                font-weight: bold;
                margin: 4px 0;
                font-family: 'Arial', sans-serif;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .date-range {
                color: #6c757d;
                font-size: 9pt;
                float: right;
                background: #e9ecef;
                padding: 3px 8px;
                border-radius: 12px;
                font-weight: 600;
                margin-top: -2px;
                border: 1px solid #00d4ff;
                font-family: 'Arial', sans-serif;
            }
            ul {
                margin: 10px 0;
                padding-left: 20px;
                font-size: 9pt;
                line-height: 1.5;
                font-family: 'Arial', sans-serif;
                color: #495057;
            }
            li {
                margin: 4px 0;
                position: relative;
            }
            li:before {
                content: "•";
                position: absolute;
                left: -12px;
                color: #00d4ff;
                font-weight: bold;
            }
            .skills-list {
                list-style: none;
                padding-left: 0;
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 8px;
            }
            .skills-list li {
                display: inline-block;
                background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
                color: #00d4ff;
                padding: 6px 12px;
                border-radius: 0;
                font-size: 9pt;
                font-weight: bold;
                border: 1px solid #00d4ff;
                font-family: 'Fira Code', monospace;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                box-shadow: 0 2px 4px rgba(0, 212, 255, 0.2);
                transition: all 0.3s ease;
                position: relative;
            }
            .skills-list li:before {
                content: "#";
                margin-right: 4px;
                color: #00d4ff;
                opacity: 0.7;
            }
            .skills-list li:hover {
                background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
                color: #1a1a1a;
                border-color: #0099cc;
            }
            p {
                margin: 8px 0;
                color: #495057;
                font-weight: 400;
                text-align: justify;
                font-family: 'Arial', sans-serif;
            }
            strong {
                font-weight: bold;
                color: #2c3e50;
                font-family: 'Arial', sans-serif;
            }
            code {
                background: #f1f3f4;
                color: #d73a49;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Fira Code', monospace;
                font-size: 9pt;
                border: 1px solid #e1e4e8;
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
