import os
import re

def remove_comments_from_python(file_path):
    """Remove comments from Python files"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove docstrings (triple quotes)
    content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
    content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)
    
    # Remove single line comments
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove comments that start at the beginning of line or after whitespace
        if line.strip().startswith('#'):
            continue
        # Remove inline comments but preserve strings
        in_string = False
        quote_char = None
        cleaned_line = ""
        i = 0
        while i < len(line):
            char = line[i]
            if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
            elif char == '#' and not in_string:
                break
            cleaned_line += char
            i += 1
        
        # Only add non-empty lines or lines with content
        if cleaned_line.strip():
            cleaned_lines.append(cleaned_line.rstrip())
    
    return '\n'.join(cleaned_lines)

def remove_comments_from_html_css(file_path):
    """Remove comments from HTML/CSS files"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # Remove CSS comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove JavaScript comments (single line)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    
    return content

def clean_file(file_path):
    """Clean comments from a file based on its extension"""
    try:
        if file_path.endswith('.py'):
            cleaned_content = remove_comments_from_python(file_path)
        elif file_path.endswith(('.html', '.css', '.js')):
            cleaned_content = remove_comments_from_html_css(file_path)
        else:
            return
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"✅ Cleaned: {file_path}")
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")

# Files to clean
files_to_clean = [
    r'c:\proyecto_sena\doit_app\views.py',
    r'c:\proyecto_sena\doit_app\models.py', 
    r'c:\proyecto_sena\doit_app\forms.py',
    r'c:\proyecto_sena\doit_app\admin.py',
    r'c:\proyecto_sena\doit_app\urls.py',
    r'c:\proyecto_sena\doit_app\templates\chat.html',
    r'c:\proyecto_sena\doit_app\templates\cliente\mis_reservas.html',
    r'c:\proyecto_sena\doit_app\templates\experto\historial_experto.html',
    r'c:\proyecto_sena\doit_app\templates\reserva.html',
    r'c:\proyecto_sena\static\css\chat.css',
    r'c:\proyecto_sena\static\css\reserva.css',
]

print("🧹 Removing comments from files...")
for file_path in files_to_clean:
    if os.path.exists(file_path):
        clean_file(file_path)
    else:
        print(f"⚠️ File not found: {file_path}")

print("✨ Comment removal completed!")
