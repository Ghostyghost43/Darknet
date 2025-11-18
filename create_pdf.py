#!/usr/bin/env python3
"""
Create a basic PDF from markdown content without external dependencies.
Uses a simple PDF structure.
"""
import re
from datetime import datetime

class SimplePDF:
    def __init__(self, title="Document"):
        self.title = title
        self.objects = []
        self.pages = []
        self.current_page = []
        self.y_position = 750  # Start near top of page
        self.page_height = 792  # Letter size
        self.page_width = 612
        self.margin = 50
        self.line_height = 14

    def add_text(self, text, font_size=11, font="Helvetica", x=None):
        """Add text to current page"""
        if x is None:
            x = self.margin

        # Check if we need a new page
        if self.y_position < 50:
            self.new_page()

        # Escape special PDF characters
        text = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

        # Split long lines
        max_width = self.page_width - (2 * self.margin)
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0
        char_width = font_size * 0.5  # Rough estimate

        for word in words:
            word_width = len(word) * char_width
            if current_width + word_width > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width + char_width

        if current_line:
            lines.append(' '.join(current_line))

        # Add all lines
        for line in lines:
            if self.y_position < 50:
                self.new_page()

            self.current_page.append(f"BT\n/{font} {font_size} Tf\n{x} {self.y_position} Td\n({line}) Tj\nET")
            self.y_position -= self.line_height

    def add_heading(self, text, level=1):
        """Add a heading"""
        font_sizes = {1: 24, 2: 20, 3: 16, 4: 14, 5: 12, 6: 11}
        font_size = font_sizes.get(level, 11)

        self.y_position -= 10  # Extra space before heading
        self.add_text(text, font_size=font_size, font="Helvetica-Bold")
        self.y_position -= 5  # Extra space after heading

    def add_code(self, code):
        """Add code block"""
        self.y_position -= 5
        lines = code.split('\n')
        for line in lines:
            if not line.strip():
                continue
            self.add_text(line, font_size=9, font="Courier", x=self.margin + 10)
        self.y_position -= 5

    def new_page(self):
        """Start a new page"""
        if self.current_page:
            self.pages.append(self.current_page)
        self.current_page = []
        self.y_position = 750

    def generate(self):
        """Generate PDF content"""
        # Add last page
        if self.current_page:
            self.pages.append(self.current_page)

        # Build PDF structure
        pdf_objects = []

        # Object 1: Catalog
        pdf_objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")

        # Object 2: Pages
        page_refs = ' '.join([f"{3+i} 0 R" for i in range(len(self.pages))])
        pdf_objects.append(f"2 0 obj\n<< /Type /Pages /Kids [{page_refs}] /Count {len(self.pages)} >>\nendobj")

        # Page objects and content
        obj_num = 3
        for page_content in self.pages:
            content_obj = obj_num + 1

            # Page object
            pdf_objects.append(
                f"{obj_num} 0 obj\n"
                f"<< /Type /Page /Parent 2 0 R /Resources << /Font << /Helvetica << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> "
                f"/Helvetica-Bold << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> "
                f"/Courier << /Type /Font /Subtype /Type1 /BaseFont /Courier >> >> >> "
                f"/MediaBox [0 0 {self.page_width} {self.page_height}] /Contents {content_obj} 0 R >>\n"
                f"endobj"
            )

            # Content object
            content = '\n'.join(page_content)
            pdf_objects.append(
                f"{content_obj} 0 obj\n"
                f"<< /Length {len(content)} >>\n"
                f"stream\n{content}\nendstream\n"
                f"endobj"
            )

            obj_num += 2

        # Build final PDF
        pdf = "%PDF-1.4\n"

        offsets = []
        for obj in pdf_objects:
            offsets.append(len(pdf))
            pdf += obj + "\n"

        # Cross-reference table
        xref_offset = len(pdf)
        pdf += "xref\n"
        pdf += f"0 {len(pdf_objects) + 1}\n"
        pdf += "0000000000 65535 f \n"
        for offset in offsets:
            pdf += f"{offset:010d} 00000 n \n"

        # Trailer
        pdf += "trailer\n"
        pdf += f"<< /Size {len(pdf_objects) + 1} /Root 1 0 R >>\n"
        pdf += "startxref\n"
        pdf += f"{xref_offset}\n"
        pdf += "%%EOF"

        return pdf

def markdown_to_pdf(md_file, pdf_file):
    """Convert markdown to PDF"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = SimplePDF("Wireshark Monitor Mode Guide")

    lines = content.split('\n')
    in_code_block = False
    code_block = []

    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if in_code_block:
                pdf.add_code('\n'.join(code_block))
                code_block = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_block.append(line)
            continue

        # Headings
        if line.startswith('######'):
            pdf.add_heading(line[7:].strip(), 6)
        elif line.startswith('#####'):
            pdf.add_heading(line[6:].strip(), 5)
        elif line.startswith('####'):
            pdf.add_heading(line[5:].strip(), 4)
        elif line.startswith('###'):
            pdf.add_heading(line[4:].strip(), 3)
        elif line.startswith('##'):
            pdf.add_heading(line[3:].strip(), 2)
        elif line.startswith('#'):
            pdf.add_heading(line[2:].strip(), 1)

        # Horizontal rule
        elif line.strip() == '---':
            pdf.y_position -= 10

        # Empty line
        elif line.strip() == '':
            pdf.y_position -= 7

        # Lists and regular text
        elif line.strip():
            # Remove markdown formatting for simplicity
            clean_line = line
            clean_line = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_line)  # Bold
            clean_line = re.sub(r'`(.+?)`', r'\1', clean_line)  # Code
            clean_line = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean_line)  # Links

            if line.startswith('- ') or line.startswith('* '):
                pdf.add_text('  • ' + clean_line[2:])
            elif re.match(r'^\d+\.', line):
                pdf.add_text('  ' + clean_line)
            elif line.startswith('> '):
                pdf.add_text('  ' + clean_line[2:], x=pdf.margin + 20)
            elif line.startswith('|'):
                # Simple table handling
                cells = [c.strip() for c in line.split('|')[1:-1]]
                pdf.add_text(' | '.join(cells), font_size=10)
            else:
                pdf.add_text(clean_line)

    pdf_content = pdf.generate()

    with open(pdf_file, 'wb') as f:
        f.write(pdf_content.encode('latin-1', errors='replace'))

    print(f"PDF created: {pdf_file}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 create_pdf.py <input.md> [output.pdf]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.md', '.pdf')

    markdown_to_pdf(input_file, output_file)
