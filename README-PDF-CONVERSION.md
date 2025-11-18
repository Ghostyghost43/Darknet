# PDF Conversion Instructions

## Quick Method: Using Your Browser

The easiest way to create a PDF from the guide:

1. **Open the HTML file**
   ```bash
   # The HTML file is already created
   xdg-open WiFi-Password-Security-Testing-Guide.html
   # or just open it in any web browser
   ```

2. **Print to PDF**
   - Press `Ctrl+P` (Windows/Linux) or `Cmd+P` (Mac)
   - In the print dialog, select "Save as PDF" or "Print to PDF"
   - Click "Save" and choose your destination

3. **Done!** You now have a professional-looking PDF

## Alternative Methods

### Method 1: Using wkhtmltopdf (Command Line)

If you have `wkhtmltopdf` installed:

```bash
wkhtmltopdf WiFi-Password-Security-Testing-Guide.html WiFi-Password-Security-Testing-Guide.pdf
```

Install wkhtmltopdf:
```bash
# Debian/Ubuntu
sudo apt install wkhtmltopdf

# macOS
brew install wkhtmltopdf

# Arch Linux
sudo pacman -S wkhtmltopdf
```

### Method 2: Using Pandoc

If you have `pandoc` and `texlive` installed:

```bash
pandoc WiFi-Password-Security-Testing-Guide.md -o WiFi-Password-Security-Testing-Guide.pdf --pdf-engine=xelatex
```

Install pandoc and LaTeX:
```bash
# Debian/Ubuntu
sudo apt install pandoc texlive-xetex texlive-fonts-recommended

# macOS
brew install pandoc
brew install --cask mactex

# Arch Linux
sudo pacman -S pandoc texlive-most
```

### Method 3: Using Chrome/Chromium Headless

If you have Chrome or Chromium installed:

```bash
# Chrome
google-chrome --headless --disable-gpu --print-to-pdf=output.pdf WiFi-Password-Security-Testing-Guide.html

# Chromium
chromium-browser --headless --disable-gpu --print-to-pdf=output.pdf WiFi-Password-Security-Testing-Guide.html
```

### Method 4: Online Converters

Upload the HTML file to:
- https://www.html-to-pdf.net/
- https://www.web2pdfconvert.com/
- https://cloudconvert.com/html-to-pdf

**Note:** Be cautious with online converters for sensitive security documentation.

## Files Included

- `WiFi-Password-Security-Testing-Guide.md` - Original markdown format
- `WiFi-Password-Security-Testing-Guide.html` - HTML version (ready for PDF conversion)
- `convert_to_html.py` - Python script used to create the HTML
- `README-PDF-CONVERSION.md` - This file

## Recommended Settings for PDF

When printing to PDF, use these settings for best results:

- **Paper Size:** A4 or Letter
- **Margins:** Default or Medium
- **Scale:** 100%
- **Background Graphics:** Enabled (for syntax highlighting)
- **Headers and Footers:** Optional

## Troubleshooting

### HTML doesn't look right
- Make sure you're opening it in a modern browser (Chrome, Firefox, Edge, Safari)
- Check that CSS is enabled
- Try a different browser

### PDF is too large
- The guide contains extensive code examples and is meant to be comprehensive
- This is normal for technical documentation

### Code blocks are cut off
- Adjust the scale to 90% or 85% when printing
- Or use landscape orientation for wide code blocks

## Need Help?

If you have issues converting to PDF, you can also use the markdown file directly. Many markdown viewers and editors support PDF export:

- **VS Code:** Install "Markdown PDF" extension
- **Typora:** File → Export → PDF
- **Obsidian:** Use the PDF export plugin
- **Marked 2 (macOS):** File → Export → PDF
