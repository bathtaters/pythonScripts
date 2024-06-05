# financeScripts
Various Python Scripts for reporting finances.

### File Descriptions
*Filename* | *Description*
-----:|:-----
**[deNester_QuickBooks.py](deNester_QuickBooks.py)** | Flatten Quickbooks' image archive
**[getAmazonReceipts.py](getAmazonReceipts.py)** | Download all Amazon yearly receipts (Uses Selenium)
**[getGmailMessages.py](getGmailMessages.py)** | Download GMail messages/attachments as PDFs (Uses Selenium)
**[getPayPalReceipts.py](getPayPalReceipts.py)** | Download PayPal yearly receipts (Uses Selenium)
**[receiptParse_main.py](receiptParse_main.py)** | Extract data from receipt PDFs and save as a CSV (Uses receiptParse_pdfOCR.py & xpdf/poppler)
**[receiptParse_pdfOCR.py](receiptParse_pdfOCR.py)** | Converts images/pdfs to text-embedded PDF/As (Uses Tesseract, pdfTk & xpdf/poppler)

### Instructions
 * Download any dependencies.
 * All scripts should be run in IDLE.
 * Configure variables at top of file then run.

### Dependencies
*Install URL* | *Install Notes*
-------------:|:----------------
[**Selenium**](https://pypi.org/project/selenium/ "Selenium install instructions") | PIP: pip install -U selenium
[**Chromedriver**](https://sites.google.com/a/chromium.org/chromedriver/downloads "Chromedriver binaries") | Download from link & move to /usr/local/bin/
[**Tesseract**](https://tesseract-ocr.github.io/tessdoc/Installation.html#macos "Tesseract install instructions") | Homebrew: brew install tesseract
[**pdfTk**](https://www.pdflabs.com/tools/pdftk-server/ "pdfTk installer") | Download from link & install
[**xpdf**](https://www.xpdfreader.com/download.html "xpdf binaries") or [**poppler**](https://poppler.freedesktop.org/ "Poppler repository") | Homebrew: brew install xpdf or brew install poppler

*Helpers* | *Description*
---------:|:----------------
[**Homebrew**](https://docs.brew.sh/Installation "Homebrew install instructions") | MacOSX package manager (To install dependencies)
[**pip**](https://pip.pypa.io/en/stable/installing/ "pip install instructions") | Python package manager (To install Python modules)
