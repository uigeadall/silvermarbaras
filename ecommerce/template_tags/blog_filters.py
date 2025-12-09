from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def format_paragraphs(value):
    """
    Convert plain text or HTML content into properly formatted paragraphs.
    Handles both plain text and HTML content intelligently.
    """
    if not value:
        return ""
    
    value_str = str(value)
    
    # Check if content has HTML tags
    has_html_tags = bool(re.search(r'<[^>]+>', value_str))
    
    if has_html_tags:
        # Content has HTML - clean it up and ensure proper formatting
        # Remove empty paragraphs
        value_str = re.sub(r'<p>\s*</p>', '', value_str, flags=re.IGNORECASE)
        # Ensure proper spacing around headings
        value_str = re.sub(r'</h([1-6])>\s*<h([1-6])>', r'</h\1>\n\n<h\2>', value_str, flags=re.IGNORECASE)
        # Ensure spacing after headings
        value_str = re.sub(r'</h([1-6])>', r'</h\1>\n\n', value_str, flags=re.IGNORECASE)
        # Clean up multiple newlines
        value_str = re.sub(r'\n\s*\n\s*\n+', '\n\n', value_str)
        return mark_safe(value_str.strip())
    
    # Plain text - convert to HTML paragraphs
    # First, normalize whitespace
    value_str = re.sub(r'\r\n', '\n', value_str)  # Windows line endings
    value_str = re.sub(r'\r', '\n', value_str)  # Mac line endings
    
    # Split by double newlines (paragraph breaks) or by sentences followed by newline
    # Try to detect if text is one big block without paragraph breaks
    if '\n\n' not in value_str and value_str.count('\n') < 3:
        # Likely one big paragraph - split by sentences
        # Split by sentence endings followed by space and capital letter
        sentences = re.split(r'([.!?])\s+([A-ZА-Я])', value_str)
        
        if len(sentences) > 3:
            # Reconstruct sentences
            paragraphs = []
            current_para = []
            
            for i in range(0, len(sentences), 3):
                if i + 1 < len(sentences):
                    sentence = sentences[i] + sentences[i+1] + ' ' + sentences[i+2]
                else:
                    sentence = sentences[i]
                
                sentence = sentence.strip()
                if sentence:
                    current_para.append(sentence)
                    
                    # Every 3-4 sentences, start a new paragraph
                    if len(current_para) >= 3:
                        paragraphs.append(' '.join(current_para))
                        current_para = []
            
            if current_para:
                paragraphs.append(' '.join(current_para))
            
            # Format as HTML paragraphs
            formatted = '\n\n'.join([f'<p>{p}</p>' for p in paragraphs if p.strip()])
            return mark_safe(formatted)
    
    # Split by double newlines (paragraph breaks)
    paragraphs = re.split(r'\n\s*\n+', value_str)
    
    formatted_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check if paragraph starts with HTML tag
        if para.startswith('<'):
            formatted_paragraphs.append(para)
        else:
            # Handle single newlines within paragraph (convert to <br>)
            lines = [line.strip() for line in para.split('\n') if line.strip()]
            if len(lines) > 1:
                para_content = '<br>'.join(lines)
            else:
                para_content = lines[0] if lines else para
            
            formatted_paragraphs.append(f'<p>{para_content}</p>')
    
    return mark_safe('\n\n'.join(formatted_paragraphs))


@register.filter
def linebreaks_to_paragraphs(value):
    """
    Convert line breaks to paragraphs. Each double line break becomes a new paragraph.
    Single line breaks become <br> tags.
    """
    if not value:
        return ""
    
    # Split by double newlines (paragraph breaks)
    paragraphs = re.split(r'\n\s*\n+', str(value))
    
    formatted = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Replace single newlines with <br>
        para = para.replace('\n', '<br>')
        formatted.append(f'<p>{para}</p>')
    
    return mark_safe('\n\n'.join(formatted))

