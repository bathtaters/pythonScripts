# financeScripts
Various Python Scripts for reporting finances.

### File Descriptions
*Filename* | *Description*
-----:|:-----
**deNester_QuickBooks.py** | Flatten Quickbooks' image archive
**getAmazonReceipts.py** | Download all Amazon yearly receipts (Uses Selenium)
**getGmailMessages.py** | Download GMail messages/attachments as PDFs (Uses Selenium)
**getPayPalReceipts.py** | Download PayPal yearly receipts (Uses Selenium)
**receiptParse_main.py** | Extract data from receipt PDFs and save as a CSV (Uses receiptParse_pdfOCR.py & xpdf/poppler)
**receiptParse_pdfOCR.py** | Converts images/pdfs to text-embedded PDF/As (Uses Tesseract, pdfTk & xpdf/poppler)

### Instructions
Download any dependencies.
All scripts should be run in IDLE.
Configure variables at top of file then run.

### Dependencies
*Name* | *Install URL* | *Install Notes*
-----:|:-----:|-----
**Selenium** | https://pypi.org/project/selenium/ | PIP: pip install -U selenium
**Chromedriver** | https://sites.google.com/a/chromium.org/chromedriver/downloads | Download & move to /usr/local/bin/
**Tesseract** | https://tesseract-ocr.github.io/tessdoc/Installation.html#macos | Homebrew: brew install tesseract
**pdfTk** | https://www.pdflabs.com/tools/pdftk-server/ | Download & install
**xpdf** OR **poppler** | https://www.xpdfreader.com/download.html OR https://poppler.freedesktop.org/ | Homebrew: brew install poppler OR xpdf
