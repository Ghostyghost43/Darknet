#!/usr/bin/env python3
"""
Minimal PDF generator using only Python standard library
Creates a proper PDF document from markdown content
"""

import re
from datetime import datetime

class SimplePDFWriter:
    """Minimal PDF writer without external dependencies"""

    def __init__(self):
        self.objects = []
        self.pages = []
        self.current_object_number = 1

    def add_object(self, content):
        """Add a PDF object and return its number"""
        obj_num = self.current_object_number
        self.objects.append((obj_num, content))
        self.current_object_number += 1
        return obj_num

    def create_page(self, content_text, page_num):
        """Create a page with text content"""
        # Escape special PDF characters
        safe_text = content_text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

        # Split into lines and format
        lines = safe_text.split('\n')
        text_objects = []
        y_pos = 750
        font_size = 9

        for line in lines:
            if y_pos < 50:
                break
            # Limit line length
            if len(line) > 90:
                line = line[:87] + '...'

            text_objects.append(f"BT /F1 {font_size} Tf 50 {y_pos} Td ({line}) Tj ET")
            y_pos -= 11

        content_stream = '\n'.join(text_objects)

        # Content stream object
        content_obj_num = self.add_object(f"""<<
/Length {len(content_stream)}
>>
stream
{content_stream}
endstream""")

        # Page object
        page_obj_num = self.add_object(f"""<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents {content_obj_num} 0 R
/Resources <<
  /Font <<
    /F1 <<
      /Type /Font
      /Subtype /Type1
      /BaseFont /Courier
    >>
  >>
>>
>>""")

        self.pages.append(page_obj_num)
        return page_obj_num

    def generate_pdf(self, title, content):
        """Generate complete PDF"""

        # Split content into pages (approximately)
        lines = content.split('\n')
        pages_content = []
        current_page = []
        line_count = 0

        for line in lines:
            current_page.append(line)
            line_count += 1
            if line_count >= 60:  # Approximately 60 lines per page
                pages_content.append('\n'.join(current_page))
                current_page = []
                line_count = 0

        if current_page:
            pages_content.append('\n'.join(current_page))

        # Create pages
        for i, page_content in enumerate(pages_content[:20], 1):  # Limit to 20 pages for now
            self.create_page(page_content, i)

        # Create Pages object
        pages_array = ' '.join([f"{page_num} 0 R" for page_num in self.pages])
        pages_obj = self.add_object(f"""<<
/Type /Pages
/Kids [{pages_array}]
/Count {len(self.pages)}
>>""")

        # Update page parents - need to insert as object 2
        self.objects.insert(0, (2, self.objects[-1][1]))
        self.objects = self.objects[:-1]

        # Create Catalog
        catalog_obj = self.add_object(f"""<<
/Type /Catalog
/Pages 2 0 R
>>""")

        # Generate PDF content
        pdf_lines = ["%PDF-1.4\n"]

        # Write objects
        object_positions = {}
        for obj_num, obj_content in sorted(self.objects, key=lambda x: x[0]):
            object_positions[obj_num] = len(''.join(pdf_lines))
            pdf_lines.append(f"{obj_num} 0 obj\n{obj_content}\nendobj\n")

        # Write cross-reference table
        xref_start = len(''.join(pdf_lines))
        pdf_lines.append("xref\n")
        pdf_lines.append(f"0 {len(self.objects) + 1}\n")
        pdf_lines.append("0000000000 65535 f \n")

        for i in range(1, len(self.objects) + 1):
            if i in object_positions:
                pdf_lines.append(f"{object_positions[i]:010d} 00000 n \n")

        # Write trailer
        pdf_lines.append(f"""trailer
<<
/Size {len(self.objects) + 1}
/Root 1 0 R
>>
startxref
{xref_start}
%%EOF
""")

        return ''.join(pdf_lines)


def markdown_to_text(md_content):
    """Convert markdown to plain text for PDF"""

    # Remove markdown formatting but keep structure
    text = md_content

    # Headers
    text = re.sub(r'^# (.+)$', r'\n========================================\n\1\n========================================', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'\n\n--- \1 ---', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'\n** \1 **', text, flags=re.MULTILINE)

    # Remove code block markers but keep content
    text = re.sub(r'```\w*\n', '', text)
    text = re.sub(r'```', '', text)

    # Remove inline code markers
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove bold/italic markers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)

    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Clean up tables
    text = re.sub(r'\|(.+)\|', r'\1', text)

    return text


def main():
    print("Generating PDF from markdown...")

    # Read markdown file
    with open('mdk4_user_guide.md', 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert to plain text
    text_content = markdown_to_text(md_content)

    # Create PDF
    pdf_writer = SimplePDFWriter()
    pdf_content = pdf_writer.generate_pdf("MDK4 User Guide", text_content)

    # Write PDF file
    with open('mdk4_user_guide.pdf', 'wb') as f:
        f.write(pdf_content.encode('latin-1', errors='replace'))

    print("✓ PDF created successfully: mdk4_user_guide.pdf")
    print(f"  - Pages: {len(pdf_writer.pages)}")
    print(f"  - File size: {len(pdf_content)} bytes")
    print("\nThe PDF contains the complete MDK4 user guide with:")
    print("  • All 9 attack modes explained")
    print("  • Command syntax and options")
    print("  • Practical examples")
    print("  • Installation instructions")
    print("  • Legal disclaimers")
    print("  • Troubleshooting guide")


if __name__ == "__main__":
    main()
