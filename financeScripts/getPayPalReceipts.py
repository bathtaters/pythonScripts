# Download PayPal yearly receipts
#  NOTE: Must have a PayPal Business account
#  NOTE: Uses Selenium + ChromeDriver
#
#  Instructions:
#    - Update Selenium
#    - Go to PayPal reports > Activity Download
#    - Choose "all activity" and CSV
#    - Open CSV and filter out transactions you don't want
#       OR
#    - Set filters using CSV FILTER below
#
#  NOTE: If you keep getting captchas, may want to try another day. 
#
#  TO GET/UPDATE SELENIUM:
#    1) Update Chrome: chrome://settings/help
#    2) Install Selenium (If not installed): https://pypi.org/project/selenium/
#    3) Download ChromeDriver (Match version to Chrome):
#       https://sites.google.com/a/chromium.org/chromedriver/downloads
#    4) Unzip ChromeDriver (Overwrite old one):
#       Terminal: sudo mv "/path/to/chromedriver" "/usr/local/bin/chromedriver"
#

# Paths
csv_in = "/path/to/Download.CSV"
out_folder = "/path/to/output/folder/"


# PayPal login info
UNAME = "username@email.com"
PWORD = None # Leave blank to open browser and ask for pword (Recommended for security)







# ---- CSV FILTER ---- #

# Only save items matching these values
ONLYS = {}
# Skip items matching any of these values
SKIPS = {
    # Template: 'SHORT_COL_NAME' : ('VALUES TO SKIP'),
    'TYPE' : (
        'Personal Payment', # This will skip Income 
        'General Withdrawal',
        'Order',
        'Shopping Cart Item',
        'General Card Deposit',
        'General Card Withdrawal',
        'General Credit Card Deposit',
        'General Credit Card Withdrawal',
        'Bank Deposit to PP Account ',
        'General Currency Conversion',
        'General Authorization',
        'Void of Authorization',
        'Account Hold for Open Authorization',
        'Reversal of General Account Hold',
        'External Hold',
        'External Release',
        'BML Credit - Transfer from BML',
        'BML Withdrawal - Transfer to BML',
        'Buyer Credit Payment Withdrawal - Transfer To BML'
    ),
    'STAT' : ('Pending','Processing'),
}
# Column name dictionary ( 'SHORT_COL_NAME' : 'Actual Name' )
COL_NAMES = {
    'URL'  : 'Transaction ID',
    'TYPE' : 'Type',
    'NAME' : 'Name',
    'DATE' : 'Date',
    'TIME' : 'Time',
    'STAT' : 'Status',
    'COL'  : 'Full Text',
}




 











# ---- ADVANCED OPTIONS ---- #

# Import stuff
import csv, os, shutil, re, json, tempfile
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


# Script Options
TEST_MODE = False # Don't actually download
DEBUG = False # Show additional output (See fmt_row below)

TEST_PPID = False # CSV Integrity check
PPID = '\ufeff' # PayPal CSV first byte ID (For integrity check)
URL_PRE = 'https://www.paypal.com/activity/payment/' # PayPal URL prefix

# Selenium Options
CHROMEDRIVER = '/usr/local/bin/chromedriver'
PG_TIMEOUT = 1000
CAPTCHA_TXT = (By.TAG_NAME,'h1','Security Challenge') # (by, by value, innerText)
PWORD_TXT = (By.ID, 'btnLogin', 'Log In')

# get_url_filename Settings
NAME_LIM = 10 # Trim name to
NAME_SUFF = 'paypal'
GEN_NAME = 'General'
NAME_RE = re.compile(r'\w*')

# Extract URL & Filename from CSV row
def get_url_filename(row,row_dict={}):
    name = ''.join(NAME_RE.findall(row[row_dict['NAME']]))[:NAME_LIM].lower()
    if DEBUG: print('NAME FOUND:',name)
    if name=='': name = GEN_NAME.lower()
    name += '_' + NAME_SUFF
    
    name += row[row_dict['URL']].strip().upper()[-4:]
    if DEBUG: print('NAME FIXED:',name)
    
    url = URL_PRE+row[row_dict['URL']]
    return (url,name)


# Format CSV row for Debug display
DEBUG_COLS = ('DATE','NAME','TYPE') # Columns to show for each row
def fmt_row(row,cols=list(COL_NAMES)):
    out_row = ''
    col_nums = [ header_row.index(COL_NAMES[c]) for c in cols if COL_NAMES[c] in header_row ]
    for c in col_nums:
        out_row += row[c] + ','
    return out_row[:-1]



























# ----- SCRIPT ----- #


def set_row_dict(header_row):
    row_dict = {}
    for name,title in COL_NAMES.items():
        cnum = -1
        if title in header_row: cnum = header_row.index(title)
        row_dict.update({ name : cnum })
    return row_dict

def set_dict(from_dict,row_dict):
    to_dict = {}
    for name,vals in from_dict.items():
        if name in row_dict and row_dict[name] >= 0:
            to_dict.update({ row_dict[name] : vals })
    return to_dict


#### SELENIUM METHODS

browser = None
DLFOLDER = tempfile.mkdtemp()
def init_browser():
    global browser

    # Save as PDF settings
    profile = {
        'savefile' : {"default_directory" : DLFOLDER},
        'printing.print_preview_sticky_settings.appState':
            json.dumps({ "recentDestinations": [{
                    "id": "Save as PDF",
                    "origin": "local",
                    "account": "",
                }],
                "selectedDestinationId": "Save as PDF",
                "version": 2
            })
    }
    browser_options = webdriver.ChromeOptions()
    browser_options.add_experimental_option('prefs', profile)
    browser_options.add_argument('--kiosk-printing')

    # OPEN BROWSER
    try:
        browser = webdriver.Chrome(CHROMEDRIVER,options=browser_options)
        browser.get(URL_PRE)
    except Exception as e:
        errmsg = '\n'.join(str(a) for a in e.args if a)
        if not errmsg: errmsg = str(e)
        return '\tSELENIUM ERROR: ' + errmsg.replace('session not created: ','').replace('\n','\n\t\t')
    
    # LOGIN
    loop = True
    while loop:
        captcha_pause()
        
        # Enter Username
        username = browser.find_element_by_id('email')
        username.send_keys(UNAME)
        browser.find_element_by_id('btnNext').click()

        captcha_pause()
        loop = enter_pword()
    
    return 0

def close_browser():
    shutil.rmtree(DLFOLDER)
    browser.quit()

def enter_pword(quick=False):
    # Enter Password
    wait_for(By.ID, 'password')
    if PWORD:
        password = browser.find_element_by_id('password')
        password.send_keys(PWORD)
        browser.find_element_by_id('btnLogin').click()
    else:
        page_pause(PWORD_TXT,'ENTER PASSWORD IN BROWSER')

    # Pause for Captcha, if none, then continue
    capt = captcha_pause()
    if not capt: return False

    # If captcha, re-enter pword
    if elem_exists(By.ID,'password'): enter_pword(True)
    if quick: return

    # If asking for email, restart loop
    if elem_exists(By.ID,'email'): return True
    return False

def txt_exists(elem):
    try:
        test = browser.find_elements(elem[0], elem[1])
    except NoSuchElementException:
        return False
    for t in test:
        try:
            if not elem[2] or elem[2].lower() in t.text.lower():
                return True
        except StaleElementReferenceException:
            return False
    return False
    
def elem_exists(by_type, type_name):
    el = browser.find_elements(by_type, type_name)
    if el: return el[0]
    return False
    
def wait_for(by_type, type_name, timeout=PG_TIMEOUT):
    return WebDriverWait(browser, timeout).until(
        EC.visibility_of_element_located((by_type, type_name)))

def page_pause(pause_elem,pause_msg='PAGE NEEDS ATTENTION'):
    paused = False
    browser.implicitly_wait(0.5)
    while txt_exists(pause_elem):
        if not paused:
            paused = True
            if pause_msg: print(' !!-',pause_msg,'-!!')
            password = elem_exists(By.ID,'password')
            if PWORD: password.send_keys(PWORD)
        browser.implicitly_wait(0.5)
    return paused

def captcha_pause():
    return page_pause(CAPTCHA_TXT,'SOLVE CHALLENGE TO CONTINUE')

def save_pdf(url):   
    browser.get(url)
    captcha_pause()
    browser.execute_script('window.print();')
    return 0


### NORMAL METHODS

def download_pdf(url, outfile):
    if TEST_MODE:
        print('URL:',url)
        return 0

    # Clean directory
    while len(os.listdir(DLFOLDER)) > 0:
        os.remove(DLFOLDER + '/' + os.listdir(DLFOLDER)[0])
    
    save_pdf(url)
    while len(os.listdir(DLFOLDER)) < 1:
        # Wait until it appears or timeout
        print('ERROR')
        return 1
    # Move file from temp dir to output
    newpdf = DLFOLDER + '/' + os.listdir(DLFOLDER)[0]
    shutil.move(newpdf,outfile)
    print('DONE')
    return 0

def get_url_iter(csv_in):
    global header_row
    with open(csv_in, newline='', encoding='utf-8') as f:
        if TEST_PPID and PPID != f.read(1):
            raise TypeError("CSV ID does not match PayPal")
        if DEBUG: print('D!CSV:',csv_in,'Opened successfully')
        table = csv.reader(f)
        header_row = next(table)
        if DEBUG: print('D!HDR:',fmt_row(header_row,DEBUG_COLS))
        row_dict = set_row_dict(header_row)
        skip_dict = set_dict(SKIPS,row_dict)
        only_dict = set_dict(ONLYS,row_dict)
        for row in table:
            if DEBUG: print('D!ROW:',fmt_row(row,DEBUG_COLS),end=' ')
            if skip_dict and any(
                row[col] in badvals for col,badvals in skip_dict.items()
                    if col>=0 ):
                if DEBUG: print('SKIPPED')
                continue
            if only_dict and not any(
                row[col] in gvals for col,gvals in only_dict.items()
                    if col>=0 ):
                if DEBUG: print('ONLY\'D')
                continue
            if DEBUG: print('SAVED')
            yield get_url_filename(row, row_dict)
    return

def main(csv_in,out_folder):

    def fix_folder(d):
        if d[-1:]!='/': d = d + '/'
        os.makedirs(d, exist_ok=True)
        return d
    
    out_folder = fix_folder(out_folder)

    print('Getting PayPal PDFs')
    if not TEST_MODE:
        er = init_browser()
        if er:
            print(er)
            return 1
    else: print('===TEST MODE ONLY, NO DOWNLOADING===')
    found = []
    
    for url,filename in get_url_iter(csv_in):
        if DEBUG: print('D!URL:',url,'\nD!FILENAME:',filename)
        if url in found:
            if DEBUG: print('D!SKIPPING: Already logged')
            continue
        found.append(url)
        print('Downloading',str(len(found)).zfill(3),filename,end='... ')
        if download_pdf(url, out_folder+filename+'.pdf'):
            print('Error on',url,filename)
            
    if not TEST_MODE: close_browser()
    print('Successfully downloaded',len(found),'pdfs.')
    return 0

main(csv_in,out_folder)



