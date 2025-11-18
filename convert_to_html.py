#!/usr/bin/env python3
"""
Simple Markdown to HTML converter with PDF-friendly styling
"""

import re
import sys

def markdown_to_html(md_content):
    """Convert markdown to HTML with basic formatting"""
    html = md_content

    # Escape HTML entities first (but preserve some markdown)
    # html = html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^##### (.*?)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)

    # Code blocks
    html = re.sub(r'```bash\n(.*?)\n```', r'<pre class="code-block bash"><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```(.*?)\n(.*?)\n```', r'<pre class="code-block"><code>\2</code></pre>', html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Bold and Italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
    html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # Horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

    # Lists (unordered)
    lines = html.split('\n')
    in_ul = False
    result = []
    for line in lines:
        if re.match(r'^- (.+)$', line):
            if not in_ul:
                result.append('<ul>')
                in_ul = True
            result.append(re.sub(r'^- (.+)$', r'<li>\1</li>', line))
        else:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            result.append(line)
    if in_ul:
        result.append('</ul>')
    html = '\n'.join(result)

    # Paragraphs
    paragraphs = html.split('\n\n')
    formatted_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<') and para != '':
            formatted_paragraphs.append(f'<p>{para}</p>')
        else:
            formatted_paragraphs.append(para)
    html = '\n\n'.join(formatted_paragraphs)

    return html

def create_html_document(content, title="WiFi Password Security Testing Guide"):
    """Wrap content in full HTML document with styling"""
    css = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }

        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            page-break-after: avoid;
        }

        h2 {
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 25px;
            page-break-after: avoid;
        }

        h3 {
            color: #555;
            margin-top: 20px;
            page-break-after: avoid;
        }

        h4 {
            color: #666;
            margin-top: 15px;
            page-break-after: avoid;
        }

        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
            color: #c7254e;
        }

        pre {
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            page-break-inside: avoid;
            margin: 15px 0;
        }

        pre code {
            background-color: transparent;
            color: #f8f8f2;
            padding: 0;
        }

        .code-block.bash {
            border-left: 4px solid #3498db;
        }

        a {
            color: #3498db;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        ul, ol {
            margin: 10px 0;
            padding-left: 30px;
        }

        li {
            margin: 5px 0;
        }

        hr {
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }

        th {
            background-color: #3498db;
            color: white;
        }

        tr:nth-child(even) {
            background-color: #f2f2f2;
        }

        .warning {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }

        .info {
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 20px 0;
        }

        @media print {
            body {
                background-color: white;
            }

            a {
                color: #000;
                text-decoration: underline;
            }

            pre {
                page-break-inside: avoid;
            }

            h1, h2, h3, h4, h5 {
                page-break-after: avoid;
            }
        }
    </style>
    """

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {css}
</head>
<body>
    {content}
</body>
</html>
"""
    return html_template

def main():
    # Read markdown file
    with open('/home/user/Darknet/WiFi-Password-Security-Testing-Guide.md', 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert to HTML
    html_content = markdown_to_html(md_content)

    # Wrap in full HTML document
    full_html = create_html_document(html_content)

    # Write to file
    with open('/home/user/Darknet/WiFi-Password-Security-Testing-Guide.html', 'w', encoding='utf-8') as f:
        f.write(full_html)

    print("HTML file created successfully!")
    print("To convert to PDF:")
    print("1. Open WiFi-Password-Security-Testing-Guide.html in your browser")
    print("2. Press Ctrl+P (or Cmd+P on Mac)")
    print("3. Select 'Save as PDF' as the destination")
    print("4. Click 'Save'")

if __name__ == '__main__':
    main()
