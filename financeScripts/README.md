# financeScripts
Various Python Scripts for reporting finances.

### File Descriptions
*Filename* | *Description*
-----:|:-----
**deNester_QuickBooks.py** | Coming soon
**flattenFolder2D.py** | Coming soon
**getAmazonReceipts.py** | Download all Amazon yearly receipts (Uses Selenium)
**getGmailMessages.py** | Download GMail messages/attachments as PDFs (Uses Selenium)
**getPayPalReceipts.py** | Coming soon
**receiptParse_main.py** | Coming soon
**receiptParse_pdfOCR.py** | Coming soon

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
