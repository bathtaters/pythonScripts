# Download all Amazon yearly receipts
#  NOTE: Uses Selenium + ChromeDriver
#
#  Instructions:
#    - Update Selenium
#    - Type in current year/username and run
#
#  TO GET/UPDATE SELENIUM:
#    1) Update Chrome: chrome://settings/help
#    2) Install Selenium (If not installed): https://pypi.org/project/selenium/
#    3) Download ChromeDriver (Match version to Chrome):
#       https://sites.google.com/a/chromium.org/chromedriver/downloads
#    4) Unzip ChromeDriver (Overwrite old one):
#       Terminal: sudo mv "/path/to/chromedriver" "/usr/local/bin/chromedriver"
#

out_folder = "/path/to/output/folder/"
year = 2020 # Year to download receipts from

# Amazon login info
UNAME = "username@email.com"
PWORD = None # Leave blank to open browser and ask for pword (Recommended for security)

# Enter array of Amazon OrderIDs to use (None will build the list for you)
#   Order ID is the string after 'orderID=' in the URL (ex. 000-0000000-0000000)
USE_LIST = None




























# ---- ADVANCED OPTIONS ---- #


# Import stuff
import os, shutil, re, json, tempfile
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


# Amazon URL prefixes
LIST_URL = 'https://www.amazon.com/gp/your-account/order-history?opt=ab&digitalOrders=1&unifiedOrders=1&orderFilter=year-'
INVOICE_URL = 'https://www.amazon.com/gp/css/summary/print.html/ref=?orderID='

# Debug modes
LIST_ONLY = False # Only get order #'s and don't save PDFs
TEST_MODE = False # Don't actually download
DEBUG = False # Additional output

# Filename setter
def get_fname(order_no):
    # Return filename from order number (w/o dashes)
    return 'amazon' + order_no[-7:] + '.pdf'


# ----- SELENIUM SETTINGS ----- #

CHROMEDRIVER = '/usr/local/bin/chromedriver' # Location of ChromeDriver
PG_TIMEOUT = 1000 # Milliseconds before Selenium gives up

NUM_XPATH = "//span[@class='a-color-secondary value']"
NEXT_CLASS = 'a-last'
DISABLED_CLASS = 'a-disabled'

# Identify when you're on the following page...
#   (by.type, type-label, innerText or '' to match anything)
PWORD_TXT = (By.CLASS_NAME,'a-form-label','Password') # Password
CAPTCHA_TXT = (By.TAG_NAME,'h4','Enter the characters you see') # Captcha
AUTH_TXT = (By.TAG_NAME,'h1','Authentication required') # 2F Auth
POSTA_TXT = (By.TAG_NAME,'h1','Check your device') # Post-authentication
ADD_MOBILE = (By.TAG_NAME,'h1','Add mobile number') # Request to add phone
ORDER_TXT = (By.TAG_NAME,'h1','Your Orders') # Order page



























# ----- SCRIPT ----- #


#### SELENIUM METHODS

browser = None
DLFOLDER = tempfile.mkdtemp()

def init_browser(first_page='about:blank'):
    global browser

    # Save as PDF settings
    profile = {
        'savefile' : {"default_directory" : DLFOLDER},
        'printing.print_preview_sticky_settings.appState':
            json.dumps({ "recentDestinations": [
                {
                    "id": "Save as PDF",
                    "origin": "local",
                    "account": "",
                }
                ],
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
        browser.get(first_page)
    except Exception as e:
        errmsg = '\n'.join(str(a) for a in e.args if a)
        if not errmsg: errmsg = str(e)
        return '\tSELENIUM ERROR: ' + errmsg.replace('session not created: ','').replace('\n','\n\t\t')
    
    # PAUSE TO LOAD
    loaded = EC.visibility_of_element_located((By.ID, 'ap_email'))
    WebDriverWait(browser, PG_TIMEOUT).until(loaded)
    captcha_pause()

    # LOGIN
    loop = True
    while loop:
        # Enter Username
        username = browser.find_element_by_id('ap_email')
        username.send_keys(UNAME)
        browser.find_element_by_id('continue').click()

        captcha_pause()
        loop = enter_pword()

    # Ignore if 'add mobile number' window
    while txt_exists(ADD_MOBILE):
        browser.find_element_by_id('ap-account-fixup-phone-skip-link').click()
        browser.implicitly_wait(3)

    #if not txt_exists(ORDER_TXT): return -1
    return 0

def enter_pword(quick=False):
    # Enter Password
    wait_for(By.ID, 'ap_password')
    if PWORD:
        password = browser.find_element_by_id('ap_password')
        password.send_keys(PWORD)
        browser.find_element_by_id('signInSubmit').click()
    else:
        page_pause(PWORD_TXT,'ENTER PASSWORD IN BROWSER')

    # Pause for Captcha, if none, then continue
    capt = captcha_pause()
    if not capt: return False

    # If captcha, re-enter pword
    if elem_exists(By.ID,'ap_password'): enter_pword(True)
    if quick: return

    # Pause for authentication
    while txt_exists(AUTH_TXT):
        page_pause(AUTH_TXT,'AUTHENTICATE TO CONTINUE')
        page_pause(POSTA_TXT,'')

    # If asking for email, restart loop
    if elem_exists(By.ID,'ap_email'): return True
    return False
    
def close_browser():
    shutil.rmtree(DLFOLDER)
    browser.quit()

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
            password = elem_exists(By.ID,'ap_password')
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

def get_element_list(xcode):
    return browser.find_elements_by_xpath(xcode)

def next_page():
    def is_disabled(elem):
        # Determine if 'Next' button has disabled class
        return DISABLED_CLASS in elem.get_attribute('class')

    # Find 'Next' Button
    next_button = None
    for e in browser.find_elements_by_class_name(NEXT_CLASS):
        if DEBUG: print('D!NEXT_CLASS_TEXT:'+e.text)
        if 'next' in e.text.lower():
            next_button = e
            break    
    if not next_button:
        print('Next button not found, check browser.')
        if (get_key('[C]ontinue running, [A]bort?', ['c','a']) == 'a'):
            return -1
    # Check if enabled
    if is_disabled(next_button):
        if DEBUG: print('D!LAST PAGE')
        return 1
    # Goto next page
    next_button.click()
    captcha_pause()
    return 0




### OTHER METHODS

def get_key(message = 'yes/no?', valid_keys = ['y','n']):
    valid_keys = [ k.lower() for k in valid_keys ]
    print(message, end=' ')
    ltr = ''
    while (not(ltr in valid_keys)):
        ltr = input(message + ' ')[0].lower()
        

def download_pdf(url, outfile):
    if TEST_MODE:
        print('URL:',url)
        return 0

    # Clean directory
    while len(os.listdir(DLFOLDER)) > 0:
        os.remove(DLFOLDER + '/' + os.listdir(DLFOLDER)[0])
    
    save_pdf(url)
    # Move file from temp dir to output
    newpdf = DLFOLDER + '/' + os.listdir(DLFOLDER)[0]
    shutil.move(newpdf,outfile)
    print('DONE')
    return 0

def get_order_num():
    while True:
        # Get list of all potential order numbers
        elem_list = get_element_list(NUM_XPATH)
        if DEBUG: print('D!NEXT PAGE:')
        for e in elem_list:
            if DEBUG: print('D!ELEM>NUM:'+e.text,end='>')
            # Test number against RegEx
            num = re.search(r'\d{3}(?:-\d{7}){2}',e.text)
            if not num:
                if DEBUG: print('[SKIP]')
                continue
            num = num.group(0)
            if DEBUG: print(num)
            yield num
        # Increment page, until last page is reached
        if next_page(): return


def main(year,out_folder,orders=None):

    def fix_folder(d):
        if d[-1:]!='/': d = d + '/'
        os.makedirs(d, exist_ok=True)
        return d

    # Initialize folder
    out_folder = fix_folder(out_folder)

    # Get list of Order numbers
    if orders: print('Using pre-defined Amazon order list')
    else: print('Getting Amazon order list...')        
    if not orders or not(TEST_MODE or LIST_ONLY):
        er = init_browser(LIST_URL+str(year))
        if er:
            print(er)
            return 1
    if not orders: orders = list(get_order_num())
    if DEBUG: print('D!ORDER LIST:',','.join(orders))
    if TEST_MODE:
        print('===TEST MODE ONLY, NO DOWNLOADING===')
        if browser: close_browser()

    if LIST_ONLY:
        if browser: close_browser()
        print(orders)
        print(len(orders),'order numbers retrieved successfully.')
        return orders
    
    found = []
    for o in orders:
        url = INVOICE_URL + o
        fname = get_fname(o)
        if DEBUG: print('D!URL:',url,'\nD!FILENAME:',fname)
        if url in found:
            if DEBUG: print('D!SKIPPING: Already logged')
            continue
        found.append(url)
        print('Downloading',str(len(found)).zfill(3),fname,end='... ')
        if download_pdf(url, os.path.join(out_folder,fname)):
            print('ERROR',url)
    if browser: close_browser()
    print('Successfully downloaded',len(found),'pdfs.')
    return 0

main(year,out_folder,USE_LIST)
