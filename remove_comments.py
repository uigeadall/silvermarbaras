
"""
Script to remove comments from Python, HTML, CSS, and JavaScript files.
Preserves docstrings and important code comments.
"""
import re
import os
import sys
from pathlib import Path

def remove_python_comments(content):
    """Remove Python comments but preserve docstrings."""
    lines = content.split('\n')
    result = []
    in_triple_quote = False
    quote_char = None
    
    for line in lines:
        stripped = line.lstrip()
        
        if not in_triple_quote:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                in_triple_quote = True
                quote_char = stripped[:3]
                result.append(line)
                continue
            elif '"""' in line or "'''" in line:
                parts = re.split(r'(""".*?""")|(\'\'\'.*?\'\'\')', line)
                new_line = ''
                for part in parts:
                    if part and (part.startswith('"""') or part.startswith("'''")):
                        new_line += part
                    elif part:
                        new_line += re.sub(r'#.*$', '', part)
                result.append(new_line)
                continue

        if in_triple_quote:
            if quote_char in line:
                in_triple_quote = False
                quote_char = None
            result.append(line)
            continue

        new_line = re.sub(r'(?<!")(?<!\')(?<!")
        if new_line.strip() or line.strip() == '':
            result.append(new_line.rstrip())
        else:
            result.append('')

    return '\n'.join(result)

def remove_html_comments(content):
    """Remove HTML comments."""
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    return content

def remove_css_comments(content):
    """Remove CSS comments."""
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    return content

def remove_js_comments(content):
    """Remove JavaScript comments."""
    lines = content.split('\n')
    result = []
    in_string = False
    string_char = None
    
    for line in lines:
        new_line = ''
        i = 0
        while i < len(line):
            char = line[i]
            
            if not in_string and char in ('"', "'"):
                in_string = True
                string_char = char
                new_line += char
            elif in_string and char == string_char and (i == 0 or line[i-1] != '\\'):
                in_string = False
                string_char = None
                new_line += char
            elif not in_string and char == '/' and i + 1 < len(line):
                if line[i+1] == '/':
                    break
                elif line[i+1] == '*':
                    i += 2
                    while i < len(line) - 1:
                        if line[i] == '*' and line[i+1] == '/':
                            i += 2
                            break
                        i += 1
                    continue
                else:
                    new_line += char
            else:
                new_line += char
            i += 1
        
        result.append(new_line)
    
    return '\n'.join(result)

def process_file(file_path):
    """Process a single file based on its extension."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        if file_path.suffix == '.py':
            content = remove_python_comments(content)
        elif file_path.suffix == '.html':
            content = remove_html_comments(content)
        elif file_path.suffix == '.css':
            content = remove_css_comments(content)
        elif file_path.suffix == '.js':
            content = remove_js_comments(content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    """Main function to process all files."""
    base_dir = Path('.')
    
    extensions = ['.py', '.html', '.css', '.js']
    exclude_dirs = {'venv', 'venv310', '.venv', 'node_modules', 'staticfiles', '.git', '__pycache__', 'migrations', 'site-packages', '.venv'}
    exclude_paths = {'magazinsrebro/.venv', 'magazinsrebro/venv', 'venv310'}
    
    files_processed = 0
    files_modified = 0
    
    for ext in extensions:
        for file_path in base_dir.rglob(f'*{ext}'):
            file_str = str(file_path)
            if any(excluded in file_str for excluded in exclude_paths):
                continue
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            files_processed += 1
            if process_file(file_path):
                files_modified += 1
                print(f"Modified: {file_path}")
    
    print(f"\nProcessed {files_processed} files, modified {files_modified} files.")

if __name__ == '__main__':
    main()

