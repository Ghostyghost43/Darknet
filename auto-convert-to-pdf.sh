#!/bin/bash

###############################################################################
# Automatic PDF Converter
# Tries multiple methods to convert Markdown/HTML to PDF
###############################################################################

echo "==================================================================="
echo "         WiFi Security Testing Guide - PDF Converter"
echo "==================================================================="
echo ""

MD_FILE="WiFi-Password-Security-Testing-Guide.md"
HTML_FILE="WiFi-Password-Security-Testing-Guide.html"
PDF_FILE="WiFi-Password-Security-Testing-Guide.pdf"

# Check if source files exist
if [ ! -f "$MD_FILE" ]; then
    echo "Error: $MD_FILE not found!"
    exit 1
fi

if [ ! -f "$HTML_FILE" ]; then
    echo "HTML file not found. Generating..."
    python3 convert_to_html.py
fi

echo "Attempting PDF conversion using available tools..."
echo ""

# Method 1: wkhtmltopdf (best quality for HTML)
if command -v wkhtmltopdf &> /dev/null; then
    echo "[1/6] Trying wkhtmltopdf..."
    wkhtmltopdf "$HTML_FILE" "$PDF_FILE" 2>/dev/null
    if [ $? -eq 0 ] && [ -f "$PDF_FILE" ]; then
        echo "✓ Success! PDF created using wkhtmltopdf"
        ls -lh "$PDF_FILE"
        exit 0
    fi
    echo "✗ wkhtmltopdf failed"
fi

# Method 2: Pandoc with LaTeX
if command -v pandoc &> /dev/null; then
    echo "[2/6] Trying pandoc with xelatex..."
    pandoc "$MD_FILE" -o "$PDF_FILE" --pdf-engine=xelatex 2>/dev/null
    if [ $? -eq 0 ] && [ -f "$PDF_FILE" ]; then
        echo "✓ Success! PDF created using pandoc + xelatex"
        ls -lh "$PDF_FILE"
        exit 0
    fi

    echo "[3/6] Trying pandoc with pdflatex..."
    pandoc "$MD_FILE" -o "$PDF_FILE" --pdf-engine=pdflatex 2>/dev/null
    if [ $? -eq 0 ] && [ -f "$PDF_FILE" ]; then
        echo "✓ Success! PDF created using pandoc + pdflatex"
        ls -lh "$PDF_FILE"
        exit 0
    fi
    echo "✗ pandoc methods failed"
fi

# Method 3: Chrome/Chromium headless
if command -v google-chrome &> /dev/null; then
    echo "[4/6] Trying Google Chrome headless..."
    google-chrome --headless --disable-gpu --print-to-pdf="$PDF_FILE" "$HTML_FILE" 2>/dev/null
    if [ $? -eq 0 ] && [ -f "$PDF_FILE" ]; then
        echo "✓ Success! PDF created using Chrome headless"
        ls -lh "$PDF_FILE"
        exit 0
    fi
    echo "✗ Chrome headless failed"
fi

if command -v chromium-browser &> /dev/null; then
    echo "[5/6] Trying Chromium headless..."
    chromium-browser --headless --disable-gpu --print-to-pdf="$PDF_FILE" "$HTML_FILE" 2>/dev/null
    if [ $? -eq 0 ] && [ -f "$PDF_FILE" ]; then
        echo "✓ Success! PDF created using Chromium headless"
        ls -lh "$PDF_FILE"
        exit 0
    fi
    echo "✗ Chromium headless failed"
fi

# Method 4: weasyprint (Python)
if command -v weasyprint &> /dev/null; then
    echo "[6/6] Trying weasyprint..."
    weasyprint "$HTML_FILE" "$PDF_FILE" 2>/dev/null
    if [ $? -eq 0 ] && [ -f "$PDF_FILE" ]; then
        echo "✓ Success! PDF created using weasyprint"
        ls -lh "$PDF_FILE"
        exit 0
    fi
    echo "✗ weasyprint failed"
fi

# All methods failed
echo ""
echo "==================================================================="
echo "  All automatic conversion methods failed or tools not available"
echo "==================================================================="
echo ""
echo "Manual conversion options:"
echo ""
echo "Option 1: Browser (EASIEST - RECOMMENDED)"
echo "  1. Open $HTML_FILE in your browser"
echo "  2. Press Ctrl+P (or Cmd+P on Mac)"
echo "  3. Select 'Save as PDF'"
echo "  4. Click Save"
echo ""
echo "Option 2: Install a conversion tool"
echo "  # For wkhtmltopdf (recommended):"
echo "  sudo apt install wkhtmltopdf"
echo "  wkhtmltopdf $HTML_FILE $PDF_FILE"
echo ""
echo "  # For pandoc + LaTeX:"
echo "  sudo apt install pandoc texlive-xetex"
echo "  pandoc $MD_FILE -o $PDF_FILE"
echo ""
echo "Option 3: Online converter"
echo "  Upload $HTML_FILE to:"
echo "  - https://www.html-to-pdf.net/"
echo "  - https://cloudconvert.com/html-to-pdf"
echo ""
echo "See README-PDF-CONVERSION.md for more details"
echo ""

exit 1
