# Download GMail messages/attachments as PDFs 
#   NOTE: Uses Selenium + ChromeDriver
#   NOTE: Only works on Mac w/ GMail account, to be run in IDLE
#
#  Instructions:
#    - Get/Update Selenium (See below)
#    - Setup GMail to allow IMAP access (See below)
#    - Fill out settings (Arrays will search multiple accounts)
#    - (OPTIONAL) Use Custom Fix Block to customize html before it is saved
#
# TO GET/UPDATE SELENIUM:
#  1) Update Chrome (If not up to date): chrome://settings/help
#  2) Install Selenium (If not installed): https://pypi.org/project/selenium/
#  2) Download ChromeDriver (Match version to Chrome):
#   https://sites.google.com/a/chromium.org/chromedriver/downloads
#  3) Unzip ChromeDriver (Overwrite old one):
#   Terminal: sudo mv "/path/to/chromedriver" "/usr/local/bin/chromedriver"
#
# TO ENABLE IMAP ACCESS ON GMAIL:
#  1) Login to GMail account
#  2) Open settings (Gear in top right > See all settings)
#  3) Open "Forwarding and POP/IMAP" tab
#  4) Under IMAP access choose "Enable IMAP"
#
# SET APPLICATION-SPECIFIC PASSWORD:
#  If you use 2FA or your password isn't working try this...
#    1) Use the following guide: https://support.google.com/accounts/answer/185833
#       - Selecting 'Other' as app (Name whatever you like)
#       - Copy the 16-char App Pasword Google gives you
#    2) Change pwords to OR enter the App Password
#    3) May need to repeat for each username
#


# SETTINGS...

# GMAIL Login
unames = ["uname1","uname2"]
pwords = [None,None]
# None = prompt user

# Gmail label/folder to use (None = Inbox)
folders = ["Label1","Label2"]

# Save to
save_to = "/path/to/output/folder/"

# Mark saved emails as read (False will leave status as is)
mark_read = False

# Convert to PDFs (False will save in original format, HTML)
make_pdf = True







# ADVANCED SETTINGS...

# EMAIL SETTINGS [NOTE: Only tested on GMail]
unread_only = True # Don't include emails marked as read
default_folder = "All Mail" # Default base folder
search_term = "UNSEEN" # UNSEEN finds unread emails
# iMap settings
host_imap = 'imap.gmail.com'
port_imap = 'default' # 'default' = 143 / 993
ssl = True


# FILE SETTINGS
remove_source = True # Removes original file when converting to PDF
wrap_txt = 100 # Word-wrap text to char count (0 = No wrap)
SKIP_LIST = ('.','..','.DS_STORE') # Files to ignore while cleaning
USEP = '_' # Spacer for attachments (emailName[USEP]attachmentName)
HTML = '.htm' # Html extension to use when creating html
ENCODER = 'latin_1' # Text Encoding/Decoding
# NOTE: latin_1 prevents crashing on non-ASCII characters

# Extensions to be converted to PDF (lower-case w/ .)
PDFABLE_EXTS = (HTML, '.htm', '.html', '.txt')

# Ignore files if they contain this prefix & suffix
addit_del_list = [ ['uber','part002.htm'], ['lyftmail','.tmp'] ]


# SELENIUM SETTINGS
CHROMEDRIVER = '/usr/local/bin/chromedriver' # Location of ChromeDriver
PG_TIMEOUT_MS = 1500 # Milliseconds before Selenium gives up
PDF = '.pdf' # Extension to use when creating PDF


# MAC LINKFILE SETTINGS
LINKEXT = '.webloc' # Linkfile extension
# save_link_file(file,URL) does: LINKFILE[0] + URL + LINKFILE[1]
LINKFILE = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n\t<key>URL</key>\n\t<string>',
            '</string>\n</dict>\n</plist>\n')
    










### CUSTOM FIX BLOCK
# Write your own fixes.
#
#   1) Create fix method
#       def CUSTOM_fix(<Filepath minus extension>):
#           return '' if no error, else return '<err string>\n' (Should ending in '\n')
#
#   2) Define fix parameters (Call fix when filename matches parameters)
#       Add to spec_list: PARAMETERS : FIX_METHOD
#       Ex. ('FILENAME_PREFIX','FILENAME_SUFFIX') : CUSTOM_fix
#
#   Helpful methods to use:
#       add_css_tags(fpath, CSS_TAGS) - See below
#       get_link(fpath, (LINK_LINE_REGEX, LINK_URL_REGEX)) - See below
#       save_link_file(fpath, LINK_URL) - Save link as a Mac link file (.webloc)
#


# Hoisted imports (So you can use them in fix methods)
### DO NOT REMOVE THESE: base64, os, re ###
import base64, os, re


# Fix method template
def sample_fix(fpath):
    # Open file for reading
    with open(fpath + HTML, 'r', 1, ENCODER) as robj:
        # Create temp file to write to
        with open(fpath + '.tmp', 'w', 1, ENCODER) as wobj:
            # Modify line by line
            for line in robj.readlines():
                wobj.write(line)
        
    # Overwrite original file with temp file
    os.remove(fpath + HTML)
    os.rename(fpath + '.tmp', fpath + HTML)

    # Add CSS tag
    add_css_tags(fpath, 'body: { background: white; }')
    
    return '' # No err


# FIX CALL PARAMETERS: spec_list
#   Methods will only be called when filename contains prefix & suffix.
#   spec_list = { 'Filename prefix', 'Filename suffix') : Method Name , etc. }
#   NOTE: Can set prefix and/or suffix as '' to match all prefixes/suffixes.
#
#   Entry Template:
#       ('prefix','suffix') : sample_fix
spec_list = { } 



# FIX HELPER METHODS
#   Use these to do common fix tasks

# Helper method to add CSS tags to file
def add_css_tags(fpath, tag_text):
    AFTER = '<style type="text/css">'

    with open(fpath + HTML, 'r', 1, ENCODER) as robj:
        with open(fpath + '.tmp', 'w', 1, ENCODER) as wobj:
            try:
                source = robj.readlines()
            except UnicodeDecodeError:
                return 'Error reading HTML file in add_css method.\n'
            for line in source:
                if AFTER.lower() in line.lower():
                    line = line + tag_text
                wobj.write(line)
                wobj.flush()
                    
    # Overwrite original file with fixed file
    os.remove(fpath + HTML)
    os.rename(fpath + '.tmp', fpath + HTML)

    return ''

# Helper method to extract a link from a page using RegEx
def get_link(fpath, regex_set):
    # EXTRACT LINK FROM HTML CODE - SAVE TO FILE
    # regex_set = [ re.compile(<MATCH LINE>), re.compile(<MATCH URL ON LINE AS GROUP 1>) ]
    # OR
    # regex_set = re.compile(<MATCH LINE w/ URL AS GROUP 1>)
    if not isinstance(regex_set, (list,tuple)): regex_set = [regex_set]
    if len(regex_set) < 2: regex_set = (regex_set[0], regex_set[0])
    for i in range(2):
        if not hasattr(regex_set[0],'search'):
            raise TypeError(str(type(regex_set[i]))+' sent as re.compile')
    
    link = None
    with open(fpath + HTML, 'r', 1, ENCODER) as robj:
        for line in robj:
            temp = regex_set[0].search(line)
            if temp:
                temp = regex_set[1].search(line)
                if temp:
                    link = temp.group(1)
                    break
    if link: return save_link_file(fpath, link)
    return None


#### END FIX BLOCK





































########## SCRIPT ##########


# Globals
import imaplib, email, getpass, tempfile, shutil
browser = None
DLFOLDER = tempfile.mkdtemp()
DEF_PORT_IMAP = [143, 993] # [ Non-SSL, SSL ]


# TO FIX:
#   Better option for duplicate files! [convert_pdf: outf]



#### SELENIUM BLOCK
import json, time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import SessionNotCreatedException


def init_browser(save_to):
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
                "version": 2,
                "marginsType": 1,
                "isHeaderFooterEnabled": False,
                "isCssBackgroundEnabled": True
            })
    }
    browser_options = webdriver.ChromeOptions()
    browser_options.add_experimental_option('prefs', profile)
    browser_options.add_argument('--kiosk-printing')

    # Open a browser window
    try:
        browser = webdriver.Chrome(CHROMEDRIVER,options=browser_options)
    except SessionNotCreatedException as e:
        errmsg = '\n'.join(str(a) for a in e.args if a)
        if not errmsg: errmsg = str(e)
        return '\tSELENIUM ERROR: ' + errmsg.replace('session not created: ','').replace('\n','\n\t\t')
    return 0

def close_browser():
    global browser
    browser.quit()
    browser = None

def wait_until_page_ready(timeout_ms = PG_TIMEOUT_MS):
    time.sleep(0.1) # prevent false-positives
    def page_ready():
        page_state = browser.execute_script('return document.readyState;')
        
        return page_state == 'complete'
    
    timeout_time = time.time() + (timeout_ms / 100)
    while time.time() < timeout_time:
        if page_ready(): return 0
        else: time.sleep(0.1)
    return 1

def save_as_pdf(infile, outfile):
    # Clean download temp directory
    while len(os.listdir(DLFOLDER)) > 0:
        os.remove(DLFOLDER + '/' + os.listdir(DLFOLDER)[0])
    
    # Open and print file
    browser.get(infile)
    if wait_until_page_ready():
        print("Error: Loading page timed out")
        return None
    browser.execute_script('window.print();')

    # Confirm file was output
    new_files = os.listdir(DLFOLDER)
    if len(new_files) != 1: return None
    new_file = os.path.join(DLFOLDER,new_files[0])

    # Move pdf to output folder
    shutil.move(new_file,outfile)
    return outfile 


#### END SELENIUM BLOCK




def split_with_quotes(inp):
    inside_quote = False
    rep_chr = '\x01'
    out = ''

    if rep_chr in inp:
        print('Error: May be invalid folder.')
    
    for i in range(len(inp)):
        c = inp[i]
        
        if c=='"': inside_quote = not(inside_quote)
        elif inside_quote and c==' ': c = rep_chr
        
        out = out + c
    
    out = out.split()

    for j in range(len(out)):
        out[j] = out[j].replace(rep_chr, ' ')

    return out

def is_file(filepath,st_end):
    # Test if file contains start and end
    i = filepath.rfind('/') + 1
    fn = str(filepath[i:])
    if fn[0]=='.': fn = fn[1:]
    end = len(st_end[1])
    if end==0: end = -len(fn)
    if fn[:len(st_end[0])]==st_end[0] and fn[-end:]==st_end[1]:
            return True
    return False   

def fix_save_dir(d):
    # Error catching
    if d[-1:]!='/': d = d + '/'
    os.makedirs(d, exist_ok=True)
    return d

def unhider(file):
    sp = list(os.path.split(os.path.split(file)[0])) + [os.path.split(file)[1]]
    # Unhide hidden file
    if sp[2][0] == '.': sp[2] = sp[2][1:]
    # Unhide from hidden dir
    if sp[1][0] == '.':
        sp[2] = sp[1][1:]+USEP+sp[2]
        sp.pop(1)
    # Commit
    if os.path.join(*sp) != file: os.rename(file,os.path.join(*sp))
    return 0

def remove_hidden_files(d):
    # Clear hidden files, in case any were missed
    
    f_list = [ os.path.join(d,f) for f in os.listdir(d) if f[0] == '.' and f not in SKIP_LIST ]
    
    for f in f_list:
        if os.path.isdir(f): shutil.rmtree(f)
        else: os.remove(f)
    
    return len(f_list)


def open_imap(host,uname,pword,ssl=True,port='default'):
    if port.lower()=='default': port = DEF_PORT_IMAP[ssl]
    port = int(port)
    
    conn = None
    if ssl: conn = imaplib.IMAP4_SSL(host)
    else: conn = imaplib.IMAP4(host)
    if not pword: pword = ask_pword(uname)
    try:
        conn.login(uname,pword)
    except imaplib.IMAP4.error as e:
        print('\t'+'\n\t'.join((arg.decode() if type(arg) is bytes else str(arg)) for arg in e.args))
        return None
    except Exception as e:
        if (len(e.args) == 0): print('\tERROR:',e)
        else:
            print('\tERROR:',','.join((arg.decode() if type(arg) is bytes else str(arg)) for arg in e.args))
        return None
    if not conn: print('\tUNKNOWN ERROR.')
    return conn

def open_folder(folder,conn):
    box = get_folder(folder,conn)
    temp = conn.select(mailbox=box)
    return temp[0]=='OK'

def set_seen(uid,conn,seen=True):
    # Set 'Read' flag to True or False
    op = ['-','+'][seen]+'FLAGS.SILENT'
    conn.uid('store', uid, op, '\\Seen')
    return seen

def get_seen(uid,conn):
    # Check if '\Seen' flag is set
    flags = conn.uid('fetch', uid, '(FLAGS)')[1][0]
    if flags == None: return False
    if '\\Seen' in flags.decode():
        return True
    return False

def remove_seen(uids,conn):
    unseen = []
    for u in uids:
        if not(get_seen(u,conn)): unseen = unseen + [u]
    return unseen

def mail_find(s,conn,unread_only=True):
    try:
        uids = conn.uid('search',None,s)[1][0].decode().split()
    except:
        print('Error: Search for ('+s+') yeilded no results.')
        return None
    if unread_only: remove_seen(uids,conn)
    return uids

def ask_pword(uname):
    return getpass.getpass('Enter password for '+uname+':')

def save_link_file(f,link):
    fn = f.replace('/.','/')+LINKEXT
    with open(fn,'w',1,ENCODER) as wobj:
        wobj.write(link.join(LINKFILE))
    return fn

def txt_to_htm(text):
    # CONVERTS TEXT (byte encoding) TO HTML (byte encoding)
    # Prepend/Append to basic text
    DEF_HTML_HEADER = '<HTML><BODY>\n'
    DEF_HTML_FOOTER = '</BODY></HTML>'
    # Characters to escape & replacements
    ESC_CHARS = [ ['&','&amp;'],
                  ['<','&lt;'],
                  ['>','&gt;'] ]
    
    def h_wrap(inp):
        # Error check user input
        if not(type(wrap_txt) is int) or wrap_txt < 5: return inp

        # Standardize line breaks
        BR = '\n'
        inp = inp.replace('\r\n',BR).replace('\r',BR)

        # Make list of where to place new linebreaks
        #   c = cursor within 'inp' ; i = cursor within line
        i = 0
        brs = [-1]
        for c in range(len(inp)):
            if inp[c]==BR: i = 0            # Reset i if linebreak.
            elif i >= wrap_txt:
                for d in range(c,0,-1):     # Overrun detected.
                    if inp[d]==BR: break
                    elif inp[d].isspace():
                        brs = brs + [d]     # Find nearest whitespace.
                        i = d - c           # Match i to c position.
                        break
                    elif d < brs[len(brs)-1] + 3:
                        brs = brs + [c]     # If no space, force break...
                        i = 0               # at 'wrap_txt'. Match i to c.
                        break               
            else: i = i + 1

        # Exit early if no new linebreaks
        if brs==[-1]: return inp

        # Split 'inp' based on new linebreaks for .join() function
        brs = brs + [len(inp)]
        j_str = [ inp[brs[j-1]+1:brs[j]] for j in range(1,len(brs)) ]
            
        return BR.join(j_str)
        
    def h_esc(inp):
        # Separate user input lists
        inc = [ i[0][0] for i in ESC_CHARS ]
        otc = [ o[1] for o in ESC_CHARS ]
        if len(inc) > len(otc): inc = inc[:len(otc)]

        # Replace chars from 'inc' list with component in 'otc' list
        out = ''
        for c in inp:
            if c in inc: out = out + otc[inc.index(c)]
            else: out = out + c
        
        return out
    
    # Matches TXT spacing (Also calls wrap() & esc())
    text = text.decode(ENCODER)
    html = DEF_HTML_HEADER
    for line in h_wrap(h_esc(text)).splitlines():
        html = html + '<pre>' + line + '</pre>\n'
    html = html + DEF_HTML_FOOTER
    
    return html.encode(ENCODER)
    

def get_folder(name,conn):
    # Set default folder to search
    default = 'INBOX'

    def parse_folder(data):
        # Retrieve last set of quotes
        # Works for GMAIL
        data = split_with_quotes(data)
        return data[len(data)-1]
    
    # Retrieve folder name
    if name=='': return default
    folders = conn.list()

    for f in folders[1]:
        f = f.decode()
        if name in f: return parse_folder(f)

    print('Error: Folder ('+name+') not found, using '+default+'.')
    return default # If fails, return default

def print_email_info(uid,conn):
    # Display email info nicely [UNUSED]
    info = get_email_info(uid,conn)

    output = '-'*8+str(info[0])+'-'*8+'\n'
    output = output + 'To: '+info[1]+'\n'
    output = output + 'From: '+info[2]+'\n'
    output = output + 'Subject: '+info[3]+'\n'
    output = output + 'Date: '+info[4]+'\n'
    output = output + 'Read: '+str(info[5])

    return output

def get_from_name(uid,conn,filesafe=True):
    # Get filename from 'From' field
    # Uses domain name minus any suffixes
    def sanitized(inp):
        import string
        # Edited from Vinko Vrsalovic on StackOverflow
        valid = '-_' + string.ascii_letters + string.digits
        inp = inp.replace(' ','_')
        return ''.join(c for c in inp if c in valid)
    
    name = get_email_info(uid,conn)[2]
    start = name.find('@') + 1
    end = name.find('.',start)
    if end < start: end = len(name) - 1
    endnew = name.find('.', end + 1)
    if endnew > end + 1:
        start = end + 1
        end = endnew
    name = name[start:end]
    if filesafe: return sanitized(name)[:12]
    return name
    

def get_email_info(uid,conn):
    # Return various info about the email [UNUSED]

    def head_decode(text):
        import email.header
        return email.header.decode_header(text)[0][0].decode(ENCODER)

    # Get message flags
    #flags = conn.uid('fetch', uid, '(FLAGS)')[1][0].decode()
    read = get_seen(uid,conn)
    
    # Get message info
    raw_email = conn.uid('fetch', uid, '(RFC822)')[1][0][1]
    email_message = email.message_from_bytes(raw_email)
    subject = email_message['Subject']
    if subject[:2]=='=?': subject = head_decode(subject)

    # Re-set \seen flag
    set_seen(uid,conn,read)
    
    return [uid, email_message['To'], email_message['From'],
            subject, email_message['Date'], read]



def save_parts(u,conn,file):

    def save_part(data,filename,not_html=False):
        # Output file
        if data=='ERR': return -1

        if not_html: data = txt_to_htm(data)

        if not os.path.exists(os.path.split(filename)[0]):
            os.mkdir(os.path.split(filename)[0])
        
        f = open(filename,mode='wb')
        f.write(data)
        f.close()
        
        return 0
        
    def get_mail(u,conn):
        # Retrieve mail object
        data = conn.uid('fetch', u, '(RFC822)')[1][0][1]
        return email.message_from_string(data.decode())

    def b64(element):
        return base64.decodebytes(element)

    def get_ext(payload):
        import mimetypes
        ext = mimetypes.guess_extension(payload.get_content_type())
        if not(ext): ext = '.bin'
        elif ext in ['.htm','.html']: return HTML
        return ext

    def first_html(f):
        if os.path.exists(f+'.htm') or os.path.exists(f+'.html'): return False
        return True
    
    # CODE ADAPTED FROM Python.org

    mail = get_mail(u,conn)
    
    # If no attachments, save just message
    if not(mail.is_multipart()):
        save_part(mail.get_payload(decode=True),
                  file+HTML, get_ext(mail) != HTML)
        if not(mark_read): set_seen(u,conn,False)
        return 1

    # Save attachments
    counter,err = 0,0
    plaintext = None
    for part in mail.walk():
        # Skip multipart containers
        if part.get_content_maintype() == 'multipart':
            continue

        # Skip plain-text message
        if part.get_content_type() == 'text/plain':
            plaintext = part
            continue
        
        message = part.get_payload(decode=True)
        
        f_suff = part.get_filename()
        sep = '_'
        if not f_suff:
            if part.get_content_type() == 'text/html' and first_html(file):
                f_suff, sep = HTML, ''
            else:
                f_suff = 'part' + str(counter+1).zfill(3) + get_ext(part)

        err = err + save_part(message, file + sep + f_suff)
        counter = counter + 1

    if counter == 0 and plaintext != None:
        message = plaintext.get_payload(decode=True)
        counter = 1 + save_part(message, file+HTML, get_ext(plaintext)!=HTML)
        
    if not(mark_read): set_seen(u,conn,False)

    return counter + err

def get_related_files(f, trunced=False):

    def get_files_walk(curdir,trunced,f_pre=None):
        f_list = []
        for f in os.listdir(curdir):
            # Include prefixes in root dir and all files in recursive dirs
            if f_pre and f[:len(f_pre)] != f_pre: continue
            elif f in SKIP_LIST: continue
            elif os.path.isdir(os.path.join(curdir,f)):
                f_list += get_files_walk(os.path.join(curdir,f),trunced)
            else:
                if trunced: f_list.append(f.replace(f_pre,''))
                else: f_list.append(os.path.join(curdir,f))
        return f_list
        
    # Find all files with prefix in dir and all files in dirs w/ prefix
    f_pre = os.path.split(f)[1]
    indir = os.path.split(f)[0]
    return get_files_walk(indir,trunced,f_pre)  


def clean_files(f, p_list=None):
    # Cleanup after PDF convert
    def is_addit(f):
        # Test if file is on the 'addit_del_list'
        for e in addit_del_list:
            if is_file(f,e): return True
        return False

    def addit_dfiles(f_list):
        # Add additional files to deletion list
        new_d = []
        for f in f_list:
            if is_addit(f): new_d = new_d + [f]
        return new_d
        
    def deleter(file):
        if not remove_source: return 0
        if not(os.path.exists(file)): return 1
        os.remove(file)
        return 0

    def unhide_files(u_files):
        def listpaths(d):
            return [ os.path.join(d,f) for f in os.listdir(d) if f not in SKIP_LIST ]
        # Un-hide files/directories recurrsively
        er = 0
        for file in u_files:
            if file in SKIP_LIST: continue
            elif os.path.isdir(file): er = er + unhide_files(listpaths(file))
            elif remove_source: er = er + unhider(file)
        return er
    
    f_list = get_related_files(f)
    er = 0

    # Remove html file plus all files on the p_list
    if p_list:
        d_files = p_list + addit_dfiles(f_list)
        if (f+HTML) in f_list: d_files = [(f+HTML)] + d_files
        d_files = list(set(d_files))
        for file in d_files: er = er + deleter(file)
    else: d_files = []

    # Show other hidden files
    u_files = list(set(f_list) - set(d_files))
    unhide_files(u_files)
    
    return er


def link_pics(f):
    # Edit HTML doc to link pictures within
    VAL = 'cid:' # Value to be replaced
    pic_re = re.compile(r'<img\s[^>]*src\s?=\s?"('+VAL+'[^"]*)"[^>]*>',re.IGNORECASE)

    def rmv_ext(fname):
        return os.path.splitext(fname)[0]

    def find_file(name, f):
        # Match filename to actual file
        rf = get_related_files(f+'_', True)

        # Fine exact matches
        exact = [ file for file in rf if rmv_ext(name) == rmv_ext(file) ]
        if len(exact) > 0: return exact[0]

        # Find matches trunc to filenames
        roughA = [ file for file in rf if rmv_ext(name)[:len(rmv_ext(file))] == rmv_ext(file) ]
        if len(roughA) > 0: return roughA[0]

        # Find matches trunc to input name
        roughB = [ file for file in rf if rmv_ext(file)[:len(rmv_ext(name))] == rmv_ext(name) ]
        if len(roughB) > 0: return roughB[0]
        
        return None # Failure

    def replace_tags(f):
        p_list = []
        er = 0
        with open(f + HTML, 'r', 1, ENCODER) as fobj:
            infile = fobj.readlines()
            with open(f + '.tmp', 'w', 1, ENCODER) as outfile:
                for line in infile:
                    pic_names = pic_re.findall(line)
                    for pic_name in pic_names:
                        new_name = find_file(pic_name.replace(VAL,''),f)
                        if new_name:
                            line = line.replace(pic_name,f+'_'+new_name)
                            p_list.append(f+'_'+new_name)
                        else: er += 1
                    outfile.write(line)
        # Overwrite original file with fixed file
        os.remove(f + HTML)
        os.rename(f + '.tmp', f + HTML)
        
        return p_list, er
        
    
    with open(f + HTML, 'r', 1, ENCODER) as fobj:
        try:
            source = fobj.readlines()
        except UnicodeDecodeError as e:
            print(' DECODE ERROR:',f+HTML,e)
            return [], 1
        
        for line in source:
            if pic_re.search(line):
                return replace_tags(f)

    return [], -1 # No VAL found


def convert_pdf(f):
    # Convert input file to PDF
    import subprocess
    FH = 'file://'
    err_return = ''

    # Build file lists
    a_list = get_related_files(f)
    p_list = []

    f_list = [ fn for fn in a_list if os.path.splitext(fn)[1].lower() in PDFABLE_EXTS ]
    
    if len(f_list) == 0: return 'No valid files.'
    if len(a_list) > 1:
        p_list, er = link_pics(f)
        if er > 0:
            err_return = err_return + str(er).zfill(2) + ' error(s) while embedding pictures.\n'
    
    for file in f_list:
        # Test if HTML must be edited, if so run editor
        if os.path.splitext(file)[1].lower() in ('.htm','.html'):
            entry = ('','')
            for e in list(spec_list.keys()):
                if is_file(f,e): entry = e
            if entry != ('',''):
                err_return = err_return + spec_list[entry](f)

        # Get filenames
        fpath = (FH + file).replace(' ','%20')
        save_as = os.path.splitext(file)[0]
        c,suff = 0,''
        while os.path.exists(save_as+suff+PDF):
            c += 1
            suff = '_'+str(c).zfill(2)

        # Print from browser
        outfile = save_as_pdf(fpath,save_as+suff+PDF)
        if outfile is None: err_return = err_return + 'ERROR: saving PDF of '+os.path.basename(file)+'\n'
    
    # Clean up
    if remove_source:
        #if os.path.exists(outf): outf = unhider(outf)
        er = clean_files(f, p_list + f_list)
        if er > 0:
            err_return = err_return + str(er).zfill(2) + ' error(s) while cleaning files.\n'

    if err_return != '': return err_return[:-1]
    return 0


def save_message(uid,save_to,conn,mark_read=True):
    # Get status of \seen flag
    read = get_seen(uid,conn)

    mod = ''
    if remove_source and make_pdf: mod = '.'

    # Filename
    name = get_from_name(uid,conn)
    if name=='': name = search_term.replace(' ','')
    file = save_to + mod + name + uid.zfill(4)

    if save_parts(uid,conn,file) > 0:
        pdferr = 0
        if make_pdf: pdferr = convert_pdf(file)
        clean_files(file)
        if pdferr != 0: return pdferr
    else: return 'Error saving message.'
    
    # Re-set \seen flag
    if not(mark_read): set_seen(uid,conn,read)

    return 0

def main(uname,pword,host_imap='imap.gmail.com',ssl=True,
         port_imap='default',folder='',search_term='',
         save_to='.',mark_read=True,unread_only=True):
    output = ''
    
    # Login to EMail server (ADD ERROR CATCHING)
    conn = open_imap(host_imap,uname,pword,ssl,port_imap)
    if conn == None: return 'Error logging in: Check connection/username/password (Or App Password if you use 2FA).'
    if not(open_folder(folder,conn)): return 'Error opening folder: '+folder

    # Search for term
    uids = mail_find(search_term,conn,unread_only)
    if uids == None:
        conn.logout()
        return 'Error: [Wrong state]'

    # Loop list of unread emails (ADD ERROR CATCHING)
    er = init_browser(save_to)
    if er: return er
    for u in uids:
        print('Saving',get_from_name(u,conn),'-',get_email_info(u,conn)[3][:40])
        msgerr = save_message(u,save_to,conn,mark_read) 
        if msgerr != 0:
            print('\t',msgerr)
            er = er + 1

    close_browser()
    conn.close()
    conn.logout()

    # Final clean-up
    remove_hidden_files(save_to)

    # Results to output
    output=output+'Found '+str(len(uids))+' unread "'+search_term+'" email(s).\n'
    output=output+'Saved messages with '+str(er)+' error(s).'

    return output

def batch():
    for i in range(len(unames)):
        print('-'*12+'\nACCOUNT:',unames[i])
        
        un = unames[i]
        if type(un) != str:
            print('Error: Invalid Username ('+str(un)+'), using blank username.')
            un = ''

        pw = None
        if not pwords or i >= len(pwords): print('No password specified, will ask user.')
        else:
            if type(pwords[i]) != str:
                print('Error: Invalid password entry ('+str(pwords[i])+'), will ask user.')
            else: pw = pwords[i]

        fldr = default_folder
        if i >= len(folders): print('ERROR: Folder not specified, using ' + default_folder)
        else:
            if type(folders[i]) != str:
                print('Error: Folder name is invalid, using ' + default_folder)
            else: fldr = folders[i] 
        
        print(main(un,pw,host_imap,ssl,port_imap,fldr,
               search_term,save_to,mark_read,unread_only))

save_to = fix_save_dir(save_to)
batch()

#set_pword("password", N) # Uncomment to encode password in position N
