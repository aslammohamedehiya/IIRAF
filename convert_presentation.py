"""
Convert Marp markdown to HTML presentation using Python
"""
import re

# Read the markdown file
with open('viva_presentation.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Create HTML presentation with reveal.js
html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IIRAF Viva Presentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/white.css">
    <style>
        .reveal h1 { font-size: 2.5em; color: #2c3e50; }
        .reveal h2 { font-size: 2em; color: #34495e; }
        .reveal h3 { font-size: 1.5em; color: #7f8c8d; }
        .reveal table { font-size: 0.7em; }
        .reveal pre { font-size: 0.6em; }
        .reveal blockquote { font-style: italic; background: #ecf0f1; padding: 20px; }
        .reveal ul { font-size: 0.9em; }
        .green-check { color: #27ae60; }
        .red-cross { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
{slides}
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            transition: 'slide',
            slideNumber: true,
            progress: true,
            center: true
        });
    </script>
</body>
</html>
"""

# Split by slide separators
slides = content.split('---\n\n')

# Convert each slide to HTML
html_slides = []
for slide in slides:
    if slide.strip():
        # Convert markdown to HTML (basic conversion)
        slide_html = slide
        
        # Headers
        slide_html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', slide_html, flags=re.MULTILINE)
        slide_html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', slide_html, flags=re.MULTILINE)
        slide_html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', slide_html, flags=re.MULTILINE)
        
        # Bold and italic
        slide_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', slide_html)
        slide_html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', slide_html)
        
        # Code blocks
        slide_html = re.sub(r'```([^`]+)```', r'<pre><code>\1</code></pre>', slide_html, flags=re.DOTALL)
        slide_html = re.sub(r'`([^`]+)`', r'<code>\1</code>', slide_html)
        
        # Checkmarks
        slide_html = slide_html.replace('✅', '<span class="green-check">✓</span>')
        slide_html = slide_html.replace('❌', '<span class="red-cross">✗</span>')
        
        # Blockquotes
        slide_html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', slide_html, flags=re.MULTILINE)
        
        # Lists
        lines = slide_html.split('\n')
        in_list = False
        new_lines = []
        for line in lines:
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                if not in_list:
                    new_lines.append('<ul>')
                    in_list = True
                new_lines.append(f'<li>{line.strip()[2:]}</li>')
            elif line.strip().startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
                if not in_list:
                    new_lines.append('<ol>')
                    in_list = True
                new_lines.append(f'<li>{line.strip()[3:]}</li>')
            else:
                if in_list:
                    new_lines.append('</ul>' if '<ul>' in '\n'.join(new_lines[-10:]) else '</ol>')
                    in_list = False
                new_lines.append(line)
        
        if in_list:
            new_lines.append('</ul>' if '<ul>' in '\n'.join(new_lines[-10:]) else '</ol>')
        
        slide_html = '\n'.join(new_lines)
        
        # Paragraphs
        slide_html = re.sub(r'\n\n', r'</p><p>', slide_html)
        
        html_slides.append(f'            <section>\n{slide_html}\n            </section>')

# Generate final HTML
final_html = html_template.format(slides='\n'.join(html_slides))

# Write HTML file
with open('viva_presentation.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("[OK] HTML presentation created: viva_presentation.html")
print("[OK] Open this file in a web browser to view your presentation")
print("[OK] Use arrow keys or space to navigate slides")
