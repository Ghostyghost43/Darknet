#!/usr/bin/env python3
"""
Simple PDF creator using only Python standard library
Creates a basic text-based PDF from the markdown content
"""

def create_simple_pdf():
    """
    Create a simple PDF using basic PDF structure
    Note: This creates a very basic PDF without external dependencies
    """

    # Read the markdown file
    with open('mdk4_user_guide.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Basic PDF structure
    # PDF header
    pdf_content = ["%PDF-1.4"]

    # Catalog object (object 1)
    catalog = """1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj"""

    # Pages object (object 2)
    pages = """2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj"""

    # Page object (object 3)
    page = """3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
  /Font <<
    /F1 5 0 R
  >>
>>
>>
endobj"""

    # Prepare content - escape special characters and format
    text_lines = []
    y_position = 750
    for line in content.split('\n')[:100]:  # Limit for basic version
        if line.strip():
            # Clean line for PDF
            clean_line = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            text_lines.append(f"BT /F1 10 Tf 50 {y_position} Td ({clean_line[:80]}) Tj ET")
            y_position -= 12
            if y_position < 50:
                break

    content_stream = "\n".join(text_lines)

    # Content object (object 4)
    contents = f"""4 0 obj
<<
/Length {len(content_stream)}
>>
stream
{content_stream}
endstream
endobj"""

    # Font object (object 5)
    font = """5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Courier
>>
endobj"""

    # Cross-reference table
    xref_positions = []
    current_pos = len("%PDF-1.4\n")

    objects = [catalog, pages, page, contents, font]
    xref_table = ["xref", "0 6", "0000000000 65535 f "]

    for obj in objects:
        xref_table.append(f"{current_pos:010d} 00000 n ")
        current_pos += len(obj) + 1

    # Trailer
    trailer = f"""trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
{current_pos}
%%EOF"""

    # Combine all parts
    full_pdf = "%PDF-1.4\n"
    full_pdf += "\n".join(objects) + "\n"
    full_pdf += "\n".join(xref_table) + "\n"
    full_pdf += trailer

    # This basic approach is too limited. Let's create a better solution
    print("Basic PDF generation is too limited with standard library alone.")
    print("Creating a printable HTML version instead...")

    return False

def create_latex_document():
    """Create a LaTeX document that can be compiled to PDF"""

    with open('mdk4_user_guide.md', 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Simple LaTeX template
    latex_content = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{tocloft}

\geometry{margin=1in}

% Code listing settings
\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    backgroundcolor=\color{gray!10},
    frame=single,
    numbers=left,
    numberstyle=\tiny\color{gray},
    keywordstyle=\color{blue},
    commentstyle=\color{green!60!black},
    stringstyle=\color{red}
}

% Header and footer
\pagestyle{fancy}
\fancyhf{}
\rhead{MDK4 User Guide}
\lhead{Page \thepage}
\rfoot{\today}

% Title
\title{\Huge\textbf{MDK4 Complete User Guide}\\
\Large Wireless Security Testing Tool}
\author{Comprehensive Reference Documentation}
\date{\today}

\begin{document}

\maketitle
\newpage

\tableofcontents
\newpage

"""

    # Convert markdown headings to LaTeX
    import re

    # Process content
    content = md_content

    # Escape LaTeX special characters
    for char in ['&', '%', '$', '#', '_', '{', '}']:
        content = content.replace(char, '\\' + char)

    content = content.replace('~', '\\textasciitilde{}')
    content = content.replace('^', '\\textasciicircum{}')

    # Convert headings
    content = re.sub(r'^# (.+)$', r'\\section{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'\\subsection{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'\\subsubsection{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'\\paragraph{\1}', content, flags=re.MULTILINE)

    # Convert code blocks
    content = re.sub(r'```bash\n(.*?)```', r'\\begin{lstlisting}[language=bash]\n\1\\end{lstlisting}', content, flags=re.DOTALL)
    content = re.sub(r'```(\w+)?\n(.*?)```', r'\\begin{lstlisting}\n\2\\end{lstlisting}', content, flags=re.DOTALL)

    # Convert inline code
    content = re.sub(r'`([^`]+)`', r'\\texttt{\1}', content)

    # Convert bold and italic
    content = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', content)
    content = re.sub(r'\*(.+?)\*', r'\\textit{\1}', content)

    # Convert lists (basic)
    content = re.sub(r'^\- (.+)$', r'\\item \1', content, flags=re.MULTILINE)

    # Add converted content
    latex_content += content

    # Close document
    latex_content += "\n\n\\end{document}"

    # Write LaTeX file
    with open('mdk4_user_guide.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print("LaTeX file created: mdk4_user_guide.tex")
    print("\nTo compile to PDF, you'll need to run:")
    print("  pdflatex mdk4_user_guide.tex")
    print("\nOr install pdflatex with:")
    print("  sudo apt-get install texlive-latex-base texlive-latex-extra")

    return True

if __name__ == "__main__":
    print("Creating LaTeX version for PDF compilation...")
    create_latex_document()
