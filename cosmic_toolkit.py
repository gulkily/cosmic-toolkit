import os
import platform
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# Font options (uncomment or add your preferred fonts)
# TITLE_FONT = 'SystemFont'
# BODY_FONT = 'SystemFont'
# TITLE_FONT = 'Helvetica-Bold'
# BODY_FONT = 'Helvetica'
TITLE_FONT = 'Times-Bold'
BODY_FONT = 'Times-Roman'

def get_system_font():
    system = platform.system()
    if system == "Darwin":  # macOS
        return "/System/Library/Fonts/Helvetica.ttc"
    elif system == "Linux":
        return "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    else:  # Windows or other
        return "C:\\Windows\\Fonts\\arial.ttf"

# Register the system font
system_font_path = get_system_font()
pdfmetrics.registerFont(TTFont('SystemFont', system_font_path))

def parse_markdown(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    chapters = []
    lines = content.split('\n')
    current_chapter = {"title": "", "body": ""}
    
    for line in lines:
        if line.startswith('# '):
            if current_chapter["title"]:
                chapters.append(current_chapter)
                current_chapter = {"title": "", "body": ""}
            current_chapter["title"] = line[2:].strip()
        elif line.startswith('## '):
            if current_chapter["title"]:
                chapters.append(current_chapter)
            current_chapter = {"title": line[3:].strip(), "body": ""}
        else:
            current_chapter["body"] += line + "\n"

    if current_chapter["title"]:
        chapters.append(current_chapter)

    return chapters

def create_zine_pdf(content, output_filename):
    # Set up the document
    page_width, page_height = A4
    c = canvas.Canvas(output_filename, pagesize=A4)
    c.setTitle("The Cosmic Toolkit: Accessible Metaphysics for Modern Seekers")

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', 
                                 fontName=TITLE_FONT, 
                                 fontSize=18, 
                                 leading=22,
                                 alignment=TA_CENTER)
    body_style = ParagraphStyle('BodyStyle', 
                                fontName=BODY_FONT, 
                                fontSize=12, 
                                leading=16,
                                alignment=TA_JUSTIFY,
                                spaceAfter=6)
    practice_style = ParagraphStyle('PracticeStyle', 
                                    fontName=BODY_FONT, 
                                    fontSize=12, 
                                    leading=16,
                                    alignment=TA_JUSTIFY,
                                    spaceAfter=6,
                                    leftIndent=20,
                                    rightIndent=20)

    # Calculate page layout
    margin = 15*mm
    content_width = (page_width - 2*margin) / 2
    content_height = (page_height - 2*margin) / 2

    def add_content_to_quarter(content, x, y, chapter_number, page_number):
        frame = Frame(x, y, content_width, content_height, leftPadding=5, bottomPadding=20, rightPadding=5, topPadding=5, id='normal')
        story = []
        
        # Add chapter number and title
        story.append(Paragraph(f"Chapter {chapter_number}", ParagraphStyle('ChapterNumber', parent=title_style, fontSize=14, spaceAfter=6)))
        story.append(Paragraph(content['title'], title_style))
        
        # Add separator
        separator = "* ~ ✧ ~ *"
        story.append(Paragraph(separator, ParagraphStyle('Separator', parent=title_style, fontSize=14, spaceAfter=12)))
        
        # Process body content
        body_parts = content['body'].split('**Practice:**')
        main_body = body_parts[0].strip()
        practice = "**Practice:** " + body_parts[1].strip() if len(body_parts) > 1 else ""
        
        # Add main body with bold text
        main_body = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', main_body)
        for paragraph in main_body.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), body_style))
        
        # Add practice section
        if practice:
            practice = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', practice)
            story.append(Paragraph(practice, practice_style))
        
        # Center content vertically
        frame.addFromList(story, c)
        
        # Add page number
        #c.setFont(BODY_FONT, 10)
        #c.drawString(x + content_width/2, y + 10, str(page_number))

    # Arrange pages for booklet printing
    arranged_pages = []
    for i in range(0, len(content), 4):
        arranged_pages.extend([content[i+3] if i+3 < len(content) else {"title": "", "body": ""},
                               content[i],
                               content[i+1] if i+1 < len(content) else {"title": "", "body": ""},
                               content[i+2] if i+2 < len(content) else {"title": "", "body": ""}])

    # Generate PDF pages
    for i in range(0, len(arranged_pages), 4):
        # Top left
        add_content_to_quarter(arranged_pages[i], margin, page_height/2, i+4, i+1)
        # Bottom left
        add_content_to_quarter(arranged_pages[i+1], margin, margin, i+1, i+1)
        # Top right
        add_content_to_quarter(arranged_pages[i+2], page_width/2, page_height/2, i+2, i+1)
        # Bottom right
        add_content_to_quarter(arranged_pages[i+3], page_width/2, margin, i+3, i+1)
        
        c.showPage()

    c.save()

# Example usage
markdown_file = "cosmic_toolkit.md"  # Replace with your .md file path
content = parse_markdown(markdown_file)
create_zine_pdf(content, "cosmic_toolkit_zine.pdf")
