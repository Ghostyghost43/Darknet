#!/usr/bin/env python3
"""
Simple Markdown to HTML converter without external dependencies
"""
import re
import html

def markdown_to_html(md_text):
    """Convert markdown to HTML"""

    # Escape HTML in the content first
    lines = md_text.split('\n')
    html_lines = []

    in_code_block = False
    in_table = False
    code_language = ""
    table_html = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_language = line[3:].strip()
                html_lines.append(f'<pre><code class="language-{code_language}">')
            else:
                in_code_block = False
                html_lines.append('</code></pre>')
            i += 1
            continue

        if in_code_block:
            html_lines.append(html.escape(line))
            i += 1
            continue

        # Tables
        if '|' in line and not in_table:
            # Start of table
            in_table = True
            table_html = ['<table border="1" cellpadding="5" cellspacing="0">']

            # Process header
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            table_html.append('<thead><tr>')
            for cell in cells:
                table_html.append(f'<th>{process_inline(cell)}</th>')
            table_html.append('</tr></thead>')

            # Skip separator line
            i += 1
            if i < len(lines) and '|' in lines[i] and '-' in lines[i]:
                i += 1

            table_html.append('<tbody>')
            continue

        if in_table and '|' in line:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            table_html.append('<tr>')
            for cell in cells:
                table_html.append(f'<td>{process_inline(cell)}</td>')
            table_html.append('</tr>')
            i += 1
            continue

        if in_table and '|' not in line:
            # End of table
            in_table = False
            table_html.append('</tbody></table>')
            html_lines.extend(table_html)
            table_html = []

        # Headings
        if line.startswith('# '):
            html_lines.append(f'<h1>{process_inline(line[2:])}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{process_inline(line[3:])}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{process_inline(line[4:])}</h3>')
        elif line.startswith('#### '):
            html_lines.append(f'<h4>{process_inline(line[5:])}</h4>')
        elif line.startswith('##### '):
            html_lines.append(f'<h5>{process_inline(line[6:])}</h5>')
        elif line.startswith('###### '):
            html_lines.append(f'<h6>{process_inline(line[7:])}</h6>')

        # Horizontal rule
        elif line.strip() == '---':
            html_lines.append('<hr>')

        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            if i > 0 and not (lines[i-1].startswith('- ') or lines[i-1].startswith('* ')):
                html_lines.append('<ul>')
            html_lines.append(f'<li>{process_inline(line[2:])}</li>')
            if i + 1 >= len(lines) or not (lines[i+1].startswith('- ') or lines[i+1].startswith('* ')):
                html_lines.append('</ul>')

        elif re.match(r'^\d+\. ', line):
            if i > 0 and not re.match(r'^\d+\. ', lines[i-1]):
                html_lines.append('<ol>')
            html_lines.append(f'<li>{process_inline(line[line.index(". ")+2:])}</li>')
            if i + 1 >= len(lines) or not re.match(r'^\d+\. ', lines[i+1]):
                html_lines.append('</ol>')

        # Blockquotes
        elif line.startswith('> '):
            html_lines.append(f'<blockquote>{process_inline(line[2:])}</blockquote>')

        # Empty line
        elif line.strip() == '':
            html_lines.append('<br>')

        # Regular paragraph
        else:
            html_lines.append(f'<p>{process_inline(line)}</p>')

        i += 1

    # Close any open table
    if in_table:
        table_html.append('</tbody></table>')
        html_lines.extend(table_html)

    return '\n'.join(html_lines)

def process_inline(text):
    """Process inline markdown elements"""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)

    # Code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)

    # Links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)

    return text

def create_html_document(body_html, title="Document"):
    """Create a complete HTML document"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        h3 {{
            color: #34495e;
            margin-top: 25px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
            color: #f8f8f2;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }}
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
{body_html}
</body>
</html>"""

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 convert_md_to_html.py <input.md> [output.html]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.md', '.html')

    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html_body = markdown_to_html(md_content)
    html_doc = create_html_document(html_body, "Wireshark Monitor Mode Pentesting Guide")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_doc)

    print(f"Converted {input_file} to {output_file}")
