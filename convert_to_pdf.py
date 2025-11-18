#!/usr/bin/env python3
"""
Simple Markdown to HTML converter for creating a printable PDF-ready document
"""

import re
import html

def markdown_to_html(md_file, html_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Convert markdown to HTML
    html_content = content

    # Headers
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)

    # Bold and italic
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)

    # Code blocks
    html_content = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html_content, flags=re.DOTALL)
    html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)

    # Links
    html_content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html_content)

    # Lists
    lines = html_content.split('\n')
    processed_lines = []
    in_ul = False
    in_ol = False

    for line in lines:
        # Unordered lists
        if re.match(r'^[\*\-\+] ', line):
            if not in_ul:
                processed_lines.append('<ul>')
                in_ul = True
            processed_lines.append('<li>' + re.sub(r'^[\*\-\+] ', '', line) + '</li>')
        elif in_ul:
            processed_lines.append('</ul>')
            in_ul = False
            processed_lines.append(line)
        # Ordered lists
        elif re.match(r'^\d+\. ', line):
            if not in_ol:
                processed_lines.append('<ol>')
                in_ol = True
            processed_lines.append('<li>' + re.sub(r'^\d+\. ', '', line) + '</li>')
        elif in_ol:
            processed_lines.append('</ol>')
            in_ol = False
            processed_lines.append(line)
        else:
            processed_lines.append(line)

    if in_ul:
        processed_lines.append('</ul>')
    if in_ol:
        processed_lines.append('</ol>')

    html_content = '\n'.join(processed_lines)

    # Paragraphs (basic)
    html_content = re.sub(r'\n\n', r'</p><p>', html_content)

    # Horizontal rules
    html_content = re.sub(r'^---$', r'<hr>', html_content, flags=re.MULTILINE)

    # Tables (basic support)
    html_content = re.sub(r'^\|(.+)\|$', lambda m: '<tr>' + ''.join(f'<td>{cell.strip()}</td>' for cell in m.group(1).split('|')) + '</tr>', html_content, flags=re.MULTILINE)

    # Full HTML document
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDK4 Complete User Guide</title>
    <style>
        @media print {{
            body {{ margin: 0.5in; }}
            h1 {{ page-break-before: always; }}
            h1:first-of-type {{ page-break-before: avoid; }}
            pre, code {{ page-break-inside: avoid; }}
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background: #fff;
        }}

        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 40px;
            font-size: 2.5em;
        }}

        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 2em;
        }}

        h3 {{
            color: #555;
            margin-top: 25px;
            font-size: 1.5em;
        }}

        h4 {{
            color: #666;
            margin-top: 20px;
            font-size: 1.2em;
        }}

        code {{
            background-color: #f4f4f4;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 2px 6px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
            color: #c7254e;
        }}

        pre {{
            background-color: #2d2d2d;
            color: #f8f8f2;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            line-height: 1.4;
            margin: 15px 0;
        }}

        pre code {{
            background: transparent;
            border: none;
            color: #f8f8f2;
            padding: 0;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}

        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        a {{
            color: #3498db;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}

        li {{
            margin: 8px 0;
        }}

        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}

        .warning {{
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}

        .info {{
            background-color: #d1ecf1;
            border-left: 5px solid #0c5460;
            padding: 15px;
            margin: 20px 0;
        }}

        strong {{
            color: #2c3e50;
        }}

        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"HTML file created: {html_file}")
    print("You can open this file in a browser and print to PDF (Ctrl+P -> Save as PDF)")

if __name__ == "__main__":
    markdown_to_html('mdk4_user_guide.md', 'mdk4_user_guide.html')
