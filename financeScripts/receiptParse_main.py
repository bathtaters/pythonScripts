# RECEIPT PARSER
# Extract data from receipt PDFs and save as a CSV
# NOTE: Uses receiptParse_pdfOCR.py for OCR (Must be in same folder to run)
#
# INSTRUCTIONS
#   - Check that you have all dependencies installed
#   - Set simple settings
#   - (Optional) Go through FILE LAYOUT to tweak settings
#   - (Optional) Open receiptParse_pdfOCR.py and tweak settings
#
#
# DEPENDENCIES:
#   receiptParse_pdfOCR.py: Place in same directory as this script
#   pdfTk: Download from https://www.pdflabs.com/tools/pdftk-server/
#   Tesseract: brew install tesseract (https://tesseract-ocr.github.io/tessdoc/Installation.html#macos)
#   pdftoppm & pdftotext (Included w/ xpdf OR poppler): brew install xpdf OR poppler
#
# FILE LAYOUT
#  - Simple Settings
#  - More Settings
#  - [No settings] Constants Block
#  - Column Settings
#  - Log Settings
#  - [No settings] Init Block
#  - Parser Settings
#  - [No settings] Script
#  

## SIMPLE SETTINGS

# Directory of PDF receipts (Can be nested in folders
inp_dir = '/path/to/receipts/'
YEAR = 2020 # Year prefix


VERBOSE = False # Print details (False only prints errors)
AUTO = 'OCR' # Do this if match not found (Keep/Skip/Abort/OCR/None) None = Ask
LOG = True # Log each PDF's activity
ALWAYS_CHOOSE = 'Generic' # Name of receipt to default to, None will ask, Skip will skip























## MORE SETTINGS
import os

# Dependencies
pdf_ocr = os.path.join(os.path.dirname(os.path.abspath(__file__)),'receiptParse_pdfOCR.py')
pdftotext = '/usr/local/bin/pdftotext'

# File options
INCLUDE_FOLDERS = False # Includes folders as their own lines in csv
CSV_FILENAME = 'ReceiptMaster'
TXT_ZS = 4 # zfill len of txt files

# Thresholds/Advanced options for text capture
GENERIC_DOLLAR_THRESHOLD = 9999 # Max amt of money expected on a receipt
MAX_HASTXT_SEARCH = 5 # Max number of lines to search for has_txt[1] (Not counting blank lines)
CAP_MIN = 1 # Linesize minimum threshold for capture
OCR_FAIL_AUTO = 'K' # If OCR fails default to ([K]eep/[S]kip/[A]bort)
BAD_CHR = '?' # Substitute for non-printable char
OCR_FORCES_CI = True # If text goes through OCR, turn on case-insensitivity regex flag


# Continue for more options...













########## CONSTANT BLOCK: DON'T EDIT ##########
import subprocess, re, shutil, sys, tempfile, datetime, importlib

# File constants
BLANK_CELL = '' # Value for empty cell
CSV_EXT = '.csv'
TXT_EXT = '.txt'
CSV_COL = ','
CSV_ROW = '\n'
# Constant dictionaries
ERR_CODES = { 0 : 'Included',
              1 : 'Included Blank Entry',
              2 : 'Skipped',
              -1 : 'Aborted' }
# Pre-defined regular expressions
DATE_SEPS = '-/'
MONTHS = ( tuple( datetime.date(2008, m+1, 1).strftime('%b') for m in range(12) ),
           tuple( datetime.date(2008, m+1, 1).strftime('%B') for m in range(12) ) )
REX_DATE_ADV = r'((?:' + '|'.join(MONTHS[0]+MONTHS[1]) + r')\s*' + \
               r'[\.' + DATE_SEPS + r']?\s*[0-3]?\d\s*' + \
               r'[' + DATE_SEPS + r"]?(?:,?\s*'?\d{2,4})?" + \
               r'|[0-3]?\d\s*[' + DATE_SEPS + r']?\s*' + \
               r'(?:'+ '|'.join(MONTHS[0]+MONTHS[1]) + r')\.?\s*' +\
               r'[' + DATE_SEPS + r"]?(?:\s*'?\d{2,4})?)"
REX = { 'DATESTR' : r"(\w{3,9}\.?\s*[0-3]?\d,?\s*'?\d{2,4})",
        'DATESTRYOPT' : r"(\w{3,9}\.?\s*[0-3]?\d,?(?:\s*'?\d{2,4})?)",
        'DATESTRICT' : REX_DATE_ADV,
        'DATENUM' : r'([01]?\d['+DATE_SEPS+r'][0-3]?\d['+DATE_SEPS+r']\d{2,4})',
        'DATENUM2' : r'([0-3]?\d['+DATE_SEPS+r']\d{1,4})',
        'DATEFLIP' : r'((?:'+str(YEAR)[:2]+')?'+str(YEAR)[2:]+'['+DATE_SEPS+r'][01]?\d['+DATE_SEPS+r'][0-3]?\d)',
        'DATENFLEX' : r'((?:\w{1,2}){1,2}['+DATE_SEPS+r']\w{1,4})',
        'PRICE' : r'(-?\$?\s*[\w,]+\.\w{2})',
        'PRICECOPT' : r'(-?\$?\s*[\w,]+(?:\.\w{2})?)',
        '1CHAR' : '^\s*(.)',
        'ALL' : r'^(.+)\s$' }

############   CONSTANT BLOCK: END   ############











## COLUMN SETTINGS

# Column Order
OUTPUT_TYPE = (None,'QBCredit','QBCheck')[0] # Choose Column order (Based on OUT_TYPES below)
OUT_TYPES = {
    # Column dupes don't work
    'QBCredit' : ('Account','Vendor','Receipt Filename','Date','Category','Total'),
    'QBCheck' : ('Account','Vendor','Receipt Filename','Date','Total','','Category')
}



# Column data: (column number : { 'Title' : column title,
#                                 'instance_var' : use this class instance var instead of receipt value
#                                 'include_rnum' : including appends reciept number if multi-receipts
#                                 '' : default value,
#                                 'Value' : 'Substitute Value'
COL_DATA = {
    0 : {
        'Title' : 'Account', # Column name
        '' : BLANK_CELL, # Default
        # Substitutions
        '0000' : 'Account Ending -0000 Name',
        'TXNBML' : 'PayPal Credit',
        'Venmo': 'Venmo',
        'Cash' : 'Cash'
    }, 1 : {
        'Title' : 'Vendor',
        'instance_var' : 'vendor_name', # Get class var "vendor_name"
        '' : BLANK_CELL,
        # Substitutions
        'Generic' : '',
        'AmazonPrime' : 'Amazon',
        'Seamless' : 'Restaurant',
        'UberTip' : 'Uber',
        'LyftTip' : 'Lyft',
        'ViaTip' : 'Via',
        'VenmoIn' : '-TBD-',
        'VenmoOut' : '-TBD-',
        'PayPalIn' : '-TBD-',
        'PayPalOut' : '-TBD-',
        'SquarePay' : '-TBD-',
    }, 2 : {
        'Title' : 'Date',
        '' : BLANK_CELL
    }, 3 : {
        'Title' : 'Category',
        'instance_var' : 'category',
        '' : BLANK_CELL,
        # Substitutions
        'TBD' : 'Uncategorized',
    }, 4 : {
        'Title' : 'Total',
        '' : BLANK_CELL
    }, 5 : {
        'Title' : '',
        'instance_var' : 'blank',
        '' : BLANK_CELL
    }, 6 : {
        'Title' : 'Folder Name',
        'instance_var' : 'folder',
        '' : BLANK_CELL
    }, 7 : {
        'Title' : 'Receipt Filename',
        'instance_var' : 'name',
        'include_rnum' : '', # Append receipt number to end of name
        '' : BLANK_CELL
    }
}













### LOG SETTINGS

LOG_COLS = ('Folder','File','Parse Method','Return Value','Error Log')
current_err_log = []
def log_format(log_arrs, root='/', *args):
    # Formats object array into array of log info (edit for custom logging)
    # May pass additional arguments via main_loop method
    # NOTE: log_arrs is array of (return value, receipt object)
    
    # Header
    out_arr = [['receiptParse log',datetime.datetime.now().isoformat().replace('T',' ')],
               [''],
               ['Additional data:']+list(args),
               ['Relative Directory:', root],
               list(LOG_COLS)]

    # Object data to include
    for code,obj in log_arrs:
        out_arr.append([ os.path.relpath(obj.path,root)+'/',
                         obj.name,
                         obj.__class__.__name__,
                         ERR_CODES.get(code,code),
                         '; '.join(obj.err_log) ])

    return out_arr




### DEBUG OPTIONS

DEBUG_OFF = True # False = Print Debug info

# Skip saving vendors not in 'only_use' (Empty will save all)
only_use = []
# Advanced debug options
DEBUG_IGN_CHRS = [[0xc2,0xa0],[0xc2,0xad]] # See 'badchr'
DEBUG_PRNT_STR = '' # See 'hasstr'
DEBUG = { 'all'      : 0,   # Print all text before capture
          'hastxt'   : 1,   # Print lines from vendor pre-search (In is_vendor())
          'hasstr'   : 0,   # Print only if line has DEBUG_PRNT_STR
          'nbytes'   : 0,   # Print first <n> bytes of line (from 'all' or 'hasstr')
          'badchr'   : 0,   # Print any removed chars + line (Ignoring DEBUG_IGN_CHRS)
          'bounds'   : 1,   # Print capture bounds
          'captured' : 0,   # Print text after capture
          'special'  : 1,   # Print info from child methods
          'backup'   : 0,   # Print original & backup dictionaries
          'parser'   : 0,   # Which parser method is used
          'lines'    : 1,   # Print lines sent for parsing
          'parsed'   : 1,   # Print parsed data
          'fixed'    : 0,   # Print row after run through fixed method
          'instance' : 0,   # Print each instance variable after assigned
          'finalcol' : 1,   # Print final column data
          'rawend'   : 0,   # Print raw object data after parsing
          'ending'   : 0 }  # Variables at end of reciept method






















######### INIT BLOCK: DON'T EDIT #########

# Check/Initialize dependicies
DEPENDS = (pdftotext,pdf_ocr) # list of dependency names
for d in DEPENDS:
    if not os.path.exists(d):
        d_str = '<UNKNOWN MODULE>'
        for k, v in list(globals().items()):
            if v is d and k != 'd':
                d_str = k
        print('FATAL ERROR: Dendancy path invalid (Or missing):',d_str,d)
        sys.exit()
pdf_ocr = os.path.split(pdf_ocr)
if pdf_ocr[0] not in sys.path: sys.path.insert(1,pdf_ocr[0])
pdf_ocr = importlib.import_module(pdf_ocr[1].replace('.py','')) 


# Render global constants
def reorder_dict(old_dict,new_order,match_key='Title'):
    new_dict = {}
    for col,col_name in enumerate(new_order):
        if not col_name: continue
        for key,val in COL_DATA.items():
            if val.get(match_key) == col_name:
                new_dict.update([(col,val)])
                break
    return new_dict

if OUTPUT_TYPE:
    CSV_FILENAME += '_' + OUTPUT_TYPE
    COL_DATA = reorder_dict(COL_DATA,OUT_TYPES[OUTPUT_TYPE],'Title')
COLS = [ COL_DATA[i]['Title'] if i in COL_DATA else '' for i in range(max(COL_DATA)+1)  ]
INSTANCE_COLS = [ i for i,d in COL_DATA.items() if 'instance_var' in d ]
BLANK_ENTRY = [BLANK_CELL]*len(COLS)

if DEBUG_OFF:
    for a in DEBUG: DEBUG[a] = 0
else: VERBOSE = True


## PARENT CLASS ##

class Receipt:
    _counter = 0            # Each child should have its own _counter at 0
    parameters = {}         # Must overload if using gen_parse()
    text_blocks = (None,None, 0)   # Unique strs to capture data w/in, capture <n> additional lines (before/after)
    has_txt = (None,None)   # For is_vendor method ((filenames,), in file <str or re.compiled>) 
    regex_flags = 0         # Python regex flags to use (Combine using | )
    category = None         # Choose category for receipt type, None will remove category row
    capture_method = 'capture_text_re' # Use this method to capture text from PDF
    parse_method = 'gen_parse_re' # Use this method to parse captured text
    backup_class = None     # Enter class to try if 'capture' method fails
    old_class = None        # Only changed by get_new_class

    # Object methods
    @classmethod
    def is_vendor(vendor,pdffile,txtfile):
        # Return: 2 = Exact Match, 1 = Partial Match, 0 = No Match
        # Test if vendor has unique_text in filename
        if vendor.has_txt[0]:
            if isinstance(vendor.has_txt[0],str):
                vendor.has_txt = ((vendor.has_txt[0],),vendor.has_txt[1])
            if not any( v.lower() in pdffile.lower() for v in vendor.has_txt[0] ):
                return 0
        
        if not(vendor.has_txt[1]) or not(os.path.exists(txtfile)):
            return 2 if vendor.has_txt[0] else 0
        
        # Test if vendor has unique_text in file
        line_count = 0
        if not txtfile:
            if DEBUG['hastxt']: print('--NO TEXT EXISTS, SKIPPING VENDOR:',vendor.__name__)
            return 1
        if DEBUG['hastxt']: print('--TEXT CHECK FOR VENDOR:',vendor.__name__)
        with open(txtfile,'rb') as f:
            for line in f:
                if line.strip() == b'': continue
                if DEBUG['hastxt']: print(line_count,str(line)[1:])
                if isinstance(vendor.has_txt[1],str):
                    if vendor.has_txt[1] in fix_line(line):
                        if DEBUG['hastxt']: print('--TEXT FOUND IN ABOVE LINE')
                        return 2
                elif hasattr(vendor.has_txt[1],'search'):
                    if vendor.has_txt[1].search(fix_line(line)):
                        if DEBUG['hastxt']: print('--TEXT FOUND IN ABOVE LINE')
                        return 2
                else: break
                if line_count > MAX_HASTXT_SEARCH: break
                line_count += 1
        return 1

    @classmethod
    def get_methods(cls):
        methods = {}
        for b in cls.__bases__:
            if b is not object: methods.update(b.__dict__)
        methods.update(cls.__dict__)
        return methods

    @staticmethod
    def get_new_class(inst, cls):
        newinst = cls(inst.name,inst.path)
        inst.__class__._counter -= 1 # Decrement old counter
        newinst.err_log = inst.err_log # Error log follows
        newinst.old_class = inst.__class__.__name__ # Set old_class
        return newinst

    @staticmethod
    def currstr_to_float(currstr):
        currflt = currstr.replace(',','').replace('$','').strip()
        if not currflt.replace('.','').isdigit(): return currstr
        return float(currflt)

    @staticmethod
    def get_title_row():
        return COLS

    @staticmethod
    def invalid_params(params):
        if len(params)<1: return True
        return any( True if len(v)!=2
                    else any(len(p)==0 for p in v)
                    for v in params.values()
                    if not callable(v) )

    def __str__(self):
        return '\n'.join(', '.join(r) for r in self.get_list())

    def __repr__(self):
        return self.get_raw_data()

    # Instance methods
    def __init__(self, name='', path=''):
        self.num = self.__class__._counter
        self.name = name
        if name == '': name = self.__class__.__name__.lower() + str(self.num).zfill(6)
        self.path = path
        self.folder = self.path
        if self.folder[-1]=='/': self.folder = self.folder[:-1]
        self.folder = os.path.split(self.folder)[1].title()
        self.blank = ' '
        
        self.vendor_name = self.__class__.__name__.replace('_',' ')
        self.category = self.category
        self.captured = None
        self.parsed = None
        self.err_log = []
        self.__class__._counter += 1

    def get_list(self):
        # Return list of parsed data
        if type(self.parsed) is not list:
            error('Get_list called before data was parsed (Ie. On skipped file)',2,True,1)
            return [['DATA NOT PARSED']]
        return self.parsed

    def get_raw_data(self):
        data = '"' + self.name + '"\n'
        data += 'Location: "' + self.path + '"\n' + 'Folder Name: "' + self.folder + '"\n'
        data += 'Vendor Name: "' + self.vendor_name + '"\n' + 'Category: "' + self.category + '"\n'
        data += 'Captured (Raw):' + '\n' + str(self.captured) + '\n'
        data += 'Parsed (Raw):' + '\n' + str(self.parsed) + '\n'
        data += 'Error Log (Raw):' + '\n'+ str(self.err_log) + '\n'
        return data

    def save_err_log(self):
        global current_err_log
        self.err_log += current_err_log
        current_err_log = []
        return self.err_log

    def get_method(self, method, default=None):
        # Return method from str, otherwise default method, otherwise None
        # Searches 'self' class and immediate parents (Skips 'object' class)
        methods = self.__class__.get_methods()
        return methods.get(method, methods.get(default, None))

    def get_instance_var(self,var_name):
        # GET 'var_name' variable
        return self.__dict__.get(var_name, '')

    def row_fix(self, row, rec_num):
        # Mess with row after it is parsed
        # row cells are referenced, row itself is NOT passed 
        return 0

    def assign_instances(self,rec_num=0):
        r = self.parsed[rec_num]
        multirec = len(self.parsed) > 1
        for i in range(len(r)):
            if i not in COL_DATA: continue
            if i in INSTANCE_COLS and (not r[i] or r[i]==BLANK_CELL):
                r[i] = self.get_instance_var(COL_DATA[i]['instance_var'])
                if r[i] and multirec and 'include_rnum' in COL_DATA[i]:
                    r[i] += '#' + str(rec_num+1).zfill(2)
                if DEBUG['instance']: print('--INSTANCE:',COLS[i],'=',r[i])
                if not r[i]:
                    error('R'+str(rec_num)+': No '+COL_DATA[i]['Title']+' found',3)
            r[i] = COL_DATA[i].get(r[i],r[i])
        return 0
    
    def capture_text(self,textfile):
        # Set self.captured to error code if needed, always return self
        for tries in range(2):
            self.captured = self.get_method(self.capture_method,Receipt.capture_method)(self,textfile)
            if DEBUG['captured']:
                if self.captured and isinstance(self.captured[0][0], (list, tuple)):
                    for i,c in enumerate(self.captured):
                        print('--CAPTURE['+str(i)+']--\n'+'--NEXT--\n'.join(''.join(r) for r in c)[:-1])
                else: print('--CAPTURED--\n'+'--NEXT--\n'.join(''.join(r) for r in self.captured)[:-1])

            # Replace <self> vars with vars from the backup class
            if not self.captured and tries < 1 and self.backup_class:
                cls = None
                for v in VENDOR_LIST:
                    if v.__name__==self.backup_class: cls = v
                if not cls: 
                    error('ERROR: Backup class for '+self.__class__.__name__+' ('+self.backup_class+') not valid.',0,True,2)
                    self.captured = -1
                    return self
                error(self.__class__.__name__+' parser failed, trying '+cls.__name__,3)
                if DEBUG['backup']: print('-----ORIG DICT:\n'+'\n'.join(' : '.join(str(p) for p in i)+' '+str(type(i[1])) for i in self.__dict__.items()))
                self = Receipt.get_new_class(self,cls)
                if DEBUG['backup']: print('------NEW DICT:\n'+'\n'.join(' : '.join(str(p) for p in i)+' '+str(type(i[1])) for i in self.__dict__.items()))
            else: break
        return self

    def append_row(self,row):
        if not row or not isinstance(row, (list,tuple)): return -1
        if not isinstance(row[0], (list, tuple)): row = (row,)
        wrote = 0
        for r in row:
            if not isinstance(r, (list,tuple)): continue
            if len(COLS) < len(r): r = r[:len(COLS)]
            for b in range(len(COLS) - len(r)):
                r.append('')
            self.parsed.append(r)
            wrote += 1
        return wrote
        
                      
    def parse(self):
        # Uses generic parser (Overloaded must set self.parsed and return exit status -1 - 2)
        ret = 0
        
        # Run general parser, return for non-zero exits
        if DEBUG['parser']: print('--PARSER USED:',self.__class__.__name__+'.'+self.get_method(self.parse_method,default).__name__)
        self.parsed = self.get_method(self.parse_method,Receipt.parse_method)(self)
        if DEBUG['parsed']: print('--PARSED: ','\n----ENTRY: '.join(' | '.join(str(i) for i in r) for r in self.parsed))
        if type(self.parsed) is int:
            ret,self.parsed = self.parsed,None
            return ret
        elif self.parsed == None: return 2
        elif self.parsed == [] or self.parsed == [['']*len(COLS)]:
            ret, self.parsed = 1, [BLANK_ENTRY[:]]
        
        # Make substitutions, includes instances and call fix method
        fix = -1
        for n,r in enumerate(self.parsed):
            fix = self.row_fix(r,n)
            if DEBUG['fixed']: print('--FIXED:',' | '.join(c for c in r))
            if fix < 0: return fix
            iret = self.assign_instances(n)
            if iret < 0: return iret
            ret = max(ret,iret)
                
        if DEBUG['finalcol']: print('--FINAL: ','\n----COL: '.join(' | '.join(r) for r in self.parsed))
        return max(ret,fix)

    def capture_text_re(self,textfile):
        # Takes 'text_blocks' used to identify bounds of actual receipt to pass to parser
        #
        # text_blocks = ( start_line, end_line, additional_lines )
        # start/end_line = regex used to identify line to begin/stop capturing
        # additional_lines = number of lines before/after start/end line to include in capture
        #
        # Value of None in start/end_line = begin/stop capture at start/end of text file
        # 0 as additional_lines does not capture start/end_line itself
        # +n includes n lines before start/after end_line (-n trims by n lines on either side)

        # NEW METHOD:
        # text_blocks = ((start_line, end_line, additional_lines),(start_line, end_line, additional_lines),...)

        # Make backwards-compatible [1/2]
        if len(self.text_blocks) > 0 and not isinstance(self.text_blocks[0], (list, tuple)):
            self.text_blocks = (self.text_blocks,)

        # Setup capture values
        size = len(self.text_blocks)
        line_re = tuple( zip(
                        *[ [ re.compile(x,self.regex_flags) if x else None
                         for x in block[:2] ] for block in self.text_blocks ]
                    ) )
        offset = [ block[2] for block in self.text_blocks ]
        buffsize = offset[:]
        self.captured, new_entry, buff = tuple( [[] for _ in range(size)] for _ in range(3) )
        
        # Open text file and find lines as defined in 'text_blocks'
        with open(textfile,'rb') as f:
            if DEBUG['all'] or DEBUG['hasstr']: print('---FILE TEXT---')
            # Setup readers at start
            reading = [ 0 if r else 1 for r in line_re[0] ]
            if 1 in reading and DEBUG['bounds']:
                print('--START['+']['.join([ str(i) for i in range(len(reading)) if reading[i] == 1 ])+'] (SOF)--')
            # Iterate through lines in textfile
            for line in f:
                line = fix_line(line)
                if DEBUG['all'] or (DEBUG['hasstr'] and DEBUG_PRNT_STR in line):
                    if DEBUG['nbytes']:
                        print(*[ "'"+line[c]+"'["+hex(ord(line[c]))+']'
                                 for c in range(min(len(line),DEBUG['nbytes'])) ],sep=',')
                    else: print(line[:-1])
                # Iterate through text_blocks setting buffers/reading lines
                for blk in range(size):
                    if buff[blk] and len(buff[blk]) == offset[blk]: buff[blk].pop(0) # trim add_lines buffer
                    if not reading[blk]:
                        if buffsize[blk] > 0: buff[blk].append(line) # build add_lines buffer
                        if line_re[0][blk] and line_re[0][blk].search(line):
                            if DEBUG['bounds']: print('--START['+str(blk)+'] (buffer:'+str(offset[blk])+')','--' if DEBUG['all'] else ': '+line[:-1])
                            new_entry[blk],reading[blk],buff[blk] = buff[blk],1,[]
                    else:
                        if line_re[1][blk] and line_re[1][blk].search(line):
                            if DEBUG['bounds']: print('---END['+str(blk)+'] (buffer:'+str(offset[blk])+')','---' if DEBUG['all'] else ': '+line[:-1])
                            reading[blk] = -1 # -1 = continue reading add_lines
                        if reading[blk] == -1 and buffsize[blk] < 1: # start new entry
                            self.captured[blk].append(new_entry[blk][-buffsize[blk]:len(new_entry[blk])+buffsize[blk]])
                            new_entry[blk],buff[blk],buffsize[blk],reading[blk] = [],[],offset[blk],0
                        elif len(line) > CAP_MIN: new_entry[blk].append(line)                        
                    if reading[blk] == -1: buffsize[blk] -= 1 # shrink add_lines end counter
            if DEBUG['bounds'] and -1 in reading:
                    print('---END['+']['.join([ str(i) for i in range(len(reading)) if reading[i] == -1 ])+'] (EOF)---')
            # Close out open readers
            for blk in range(size):
                if reading[blk] == -1 or (new_entry[blk] and not line_re[1][blk]):
                    self.captured[blk].append(new_entry[blk][-min(offset[blk],0):len(new_entry[blk])+offset[blk]]) # save last new_entry
        if DEBUG['all'] or DEBUG['hasstr']: print('---END FILE---')
        
        # Make backwards-compatible [2/2]
        if size == 1 and len(self.captured) == 1: self.captured = self.captured[0]
        else:
            for e in self.captured:
                if not e: e.append([])
        
        return self.captured

    def gen_parse_re(self):        
        # GENERAL PARSER USING REGULAR EXPRESSIONS AS INPUT
        #
        # params = dictionary with column name defining line_ids and info_params
        #    ex. params = { 'Column' : ((line_id), text_id)  }
        #
        # line_id = (Unique identifier, Target line offset, Use First Match (= False)) 
        #       NOTE: Blank lines are not counted! 
        #   Unique identifier:
        #       '<regex>' = find line containing regular expression
        #       <int> = line count from first line (1st = 0)
        #       -<int> = line count from last line
        #   Target line offset: <int>
        #       parse n lines before (-n) or after (+n) unique id is found
        #   Use First Match: (Only applies when using '<regex>', can leave blank)
        #       False = (Default) Use last regex line match found
        #       True = Use first regex line match found
        #
        # text_id = '<regex>'
        #   Apply findall.(regex) to line, return 1st group from 1st match
        #   ('<regex>', True) = return last non-overlapping instance of <regex>
        #
        # params can also be { 'Column' : custom_method }
        #       custom_method should accept (self, reciept_num)
        #       and should return value of 'Column' for receipt_num
        #           <str> = value found as str
        #           None = no value found
        #           -1 (int) = abort program (make error call yourself)

        # Check if parameters are valid [DOES THIS WORK??]
        if Receipt.invalid_params(self.parameters):
            error('ERROR: Invalid parameters for receipt type '+self.__class__.__name__,3)
            return -1
        
        # Setup variables
        custom = [ i for i,c in enumerate(COLS) if callable(self.parameters.get(c)) ]
        items = [ c for c in list(enumerate(COLS))
                  if (c[1] in self.parameters
                  and c[0] not in INSTANCE_COLS + custom ) ]
        line_ids = [ (i,c,re.compile(self.parameters[c][0][0],self.regex_flags))
                     for i,c in items if isinstance(self.parameters[c][0][0],str) ]

        # Combine capture bounds (If new capt method used)
        if self.captured and isinstance(self.captured[0][0], (list, tuple)):
                capt_combo = []
                for capt in self.captured:
                    for r,rec in enumerate(capt):
                            if r >= len(new): capt_combo.append(rec)
                            else: capt_combo[r] += rec
                self.captured = capt_combo
            
        
        # Go through each receipt
        info = []
        for e,rec in enumerate(self.captured):
            newinfo = ['']*len(COLS)

            # Determine lines to parse
            lines = [None]*len(COLS)
            for i,c in items:
                # Integer method
                if isinstance(self.parameters[c][0][0],int):
                    if self.parameters[c][0][0] < 0:
                        lines[i] = len(rec) + self.parameters[c][0][0] + self.parameters[c][0][1]
                    else: lines[i] = self.parameters[c][0][0] + self.parameters[c][0][1]

            # Search for line regex
            if len(line_ids) > 0:
                for ln in range(len(rec)):
                    for i,c,r in line_ids:
                        if r.search(rec[ln]):
                            if lines[i] and len(self.parameters[c][0]) > 2 and self.parameters[c][0][2]:
                                # Skip if a match has been made before and "Use First Match" = True
                                pass
                            else: lines[i] = ln + self.parameters[c][0][1]

            # Apply regex for each item found
            for i,ln in enumerate(lines):
                if i in INSTANCE_COLS + custom: continue
                if ln == None:
                    error(('R'+str(e)+':',COLS[i],'line not found'),3)
                    continue

                if DEBUG['lines']: print('--PARSE LINE (R'+str(e),COLS[i]+'):',rec[min(ln,len(rec)-1)][:-1])
                text_id, last = self.parameters[COLS[i]][1], False
                
                if type(text_id) in (list,tuple): text_id,last = text_id[0],True
                if not isinstance(text_id,str):
                    error(('R'+str(e)+':',COLS[i],'text ID invalid'),3)
                    continue

                if ln >= len(rec): ln = len(rec) - 1
                matches = re.findall(text_id,rec[ln],self.regex_flags)
                
                # Add item to list
                use_match = 0
                if len(matches) <= use_match:
                    error(('R'+str(e)+':',COLS[i],'text not found'),3)
                    continue
                if last: use_match = len(matches) - 1

                newinfo[i] = matches[use_match]

            # Run custom methods
            for c in custom:
                newinfo[c] = self.parameters[COLS[c]](self,e)
                if not newinfo[c]:
                    newinfo[c] = ''
                    error(('R'+str(e)+':',COLS[c],'not found'),3)
                elif isinstance(newinfo[c],int):
                    error(('R'+str(e)+':',COLS[c],'custom parser',self.parameters[COLS[c]].__name__,'failed'),2)
                    return newinfo[c]
            
            # Add list to master list
            info.append(newinfo)

        return info



## Fallback Parser settings

class Generic(Receipt):
    has_txt = (None,None)
    _counter = 0
    category = 'TBD'

    regex_flags = re.I
    text_blocks = (None,None,0)

    parameters = { 'Account' : None,
                   'Date' : ( (REX['DATEFLIP']+r'\D|'+REX['DATENUM']+r'\D|'+REX['DATESTRICT']+r'\D',0,True),
                               REX['DATEFLIP']+'|'+REX['DATENUM']+'|'+REX['DATESTRICT'] ),
                   'Total' : None }
                   
    def get_acct(self,rec_num):
        # Get all CC numbers on receipt
        cards = []
        card_re = re.compile(r'\D\s?(\d{4})\s?\D',self.regex_flags)
        for line in self.captured[rec_num]:
            cards += card_re.findall(line)

        # Find if value is in COL_DATA already
        if len(cards) < 1: return None
        for cc in cards:
            if cc in COL_DATA[COLS.index('Account')]: return cc
        return cards[max(len(cards)-2,0)]
    parameters['Account'] = get_acct
        
    def get_price(self,rec_num):
        # Get all prices on receipt
        prices = []
        price_re = re.compile(REX['PRICE'],self.regex_flags)
        for line in self.captured[rec_num]:
            prices += price_re.findall(line)
        prices = [ Receipt.currstr_to_float(p) for p in prices ] + [0.0]

        # Choose the largest one
        price = str(max( abs(round(p*100)) for p in prices if isinstance(p,float) and p < GENERIC_DOLLAR_THRESHOLD ))
        if price == '0': return None

        # Convert to USD str
        for i in range(len(price)-5,0,-3):
            price = price[:i] + ',' + price[i:]
        return '$' + price[:-2] + '.' + price[-2:]
    parameters['Total'] = get_price

    def row_fix(self,row,rec_num):
        date_row = COLS.index('Date')
        for i in range(len(row)):
            # Replace any type of whitespace w/ single space
            if isinstance(row[i],str):
                row[i] = ' '.join(row[i].split())
            # Append year to end of date row (If not already)
            if i == date_row:
                if type(row[i]) is tuple:
                    if row[i][2]: row[i] = row[i][2]
                    elif row[i][0]: row[i] = flip_year(row[i][0])
                    else: row[i] = row[i][1]
                row[i] = append_year(row[i])
        return 0
    
############   INIT BLOCK: END   ############














## PARSER SETTINGS

class Amazon(Receipt):
    has_txt = ('amazon',None)
    _counter = 0

    parse_method = 'amazon_parse'
    parameters = { 'Account' : (' ending in ',':'),
                    'Date' : (':', (':',True)),
                    'Total' : ((':',True), 0) }
    # text_block[0] = main block, [1] = date at top
    text_blocks = ((r'^Payment Method:\s',
                    r'^To view the status of your order, return to Order Summary.',1),
                   (r'^Print this page for your records',r'^Items Ordered',0))
    category = 'TBD'

    test = 'ending in'
    altpay_terms = ('Rewards Points','Gift Card Amount') #'Courtesy Credit')
    altpay_re = tuple( re.compile(term+':\s*'+REX['PRICE']) for term in altpay_terms )
    altpay_account = 'Cash'
    altpay_date = ''

    date_spec = re.compile(r'Order Placed:\s'+REX['DATESTR'])
    def get_amazon_date(self,rec=0):
        for ln in self.captured[1][rec]:
            dt = self.date_spec.search(ln)
            if dt: return dt.group(1).strip()
        return ''

    def row_fix(self,row,rec_num):
        if not row[COLS.index('Date')]: row[COLS.index('Date')] = self.get_amazon_date(rec_num)
        return 0
    
    def amazon_parse(self):
        # De-nest
        flat_data = []
        for d in self.captured[0]:
            flat_data = flat_data + d

        # Split lines / remove lines w/o 'test'
        charges,altpay = [],[]
        for ln in flat_data:
            s = ln.count(Amazon.test)
            if s < 1:
                # Check for alternate methods of pay
                for altmeth_re in self.altpay_re:
                    altmeth = altmeth_re.search(ln)
                    if altmeth: altpay.append(altmeth.group(1).replace('-',''))
                continue
            elif s == 1:
                charges.append(ln[:-1])
                continue

            split = len(ln)-1
            for i in range(s):
                a = ln.rfind(Amazon.test, 0, split)
                if a < 0: break
                b = ln.rfind('$', 0, a)
                c = -1
                if b >= 0:
                    c = ln.find(' ',b)
                    if c < 0: break
                charges.append(ln[c+1:split])
                split = c
    
        # Find info w/in line
        info = []
        if DEBUG['special']: print('-AMZN: Found',len(charges),'charge(s) and',len(altpay),'non-card payment(s).')
        for e,c in enumerate(charges):
            newinfo = ['']*len(COLS)
            for i in ( c for n,c in enumerate(COLS) if n not in INSTANCE_COLS ):
                if i not in Amazon.parameters:
                    if i: error('No parameters for '+i+' in Amazon, skipping',3)
                    continue
                bounds = []
                for j in range(2):
                    p = Amazon.parameters[i][j]
                    if type(p) is str: p = (p, False)
                    if type(p) is int:
                        if p > 0: bounds.append(p)
                        elif p == 0:
                            if j == 0: bounds.append(0)
                            elif j == 1: bounds.append(len(c))
                        else: bounds.append(len(c) + p)
                    elif type(p) is list or type(p) is tuple:
                        if type(p[0]) is not str or type(p[1]) is not bool:
                            if VERBOSE: print('\t',end='')
                            error(('FATAL PARAM ERR R#'+str(e),'<Amazon>',p,COLS[i]),2,True,1)
                            return -1
                        newbound = -1
                        if p[1]: newbound = c.rfind(p[0])
                        else: newbound = c.find(p[0])
                        if newbound < 0:
                            error(('Text not found for R'+str(e),COLS[i]),3)
                        else:
                            if j == 0: newbound = newbound + len(p[0])
                            bounds.append(newbound)
                    
                newinfo[COLS.index(i)] = c[bounds[0]:bounds[1]].strip()
            info.append(newinfo)

        
        
        
        # Append 'points' transactions at bottom (Using account specified above)
        if altpay:
            # Get date
            altpay_date = info[0][COLS.index('Date')] if info else self.get_amazon_date(0) # Get date at top of receipt
            if DEBUG['special'] and not info: print('-AMZN: No transaction date, using top date. ('+altpay_date+')')
            for a in altpay:
                newinfo = ['']*len(COLS)
                newinfo[COLS.index('Date')] = altpay_date
                newinfo[COLS.index('Account')] = self.altpay_account
                newinfo[COLS.index('Total')] = a
                info.append(newinfo)
                
        return info # Return to parse Parent method




class AmazonPrime(Receipt):
    has_txt = ('amazonpn',None)
    _counter = 0
    category = 'TBD'

    text_blocks = (r'^Delivery time',
                    r'^Payment method',3)
    parameters = { 'Account' : ((r'^ending in',0),r'(\d{4})\s$'),
                    'Date' : ((0,3), REX['DATENUM']),
                    'Total' : ((0,0), REX['PRICE']+r'\s$') }


class Lyft(Receipt):
    has_txt = ('LyftMail',
               re.compile('.{0,2}'.join('Thanksforridingwith')))
    _counter = 0
    category = 'Car'

    parameters = { 'Account' : ((r'\w\s\*\d{4}',0),r'\s\*(\d{4})\s'),
                    'Date' : ((0,0), r'^'+REX['DATESTR']+r'\s+AT\s'),
                    'Total' : ((r'^'+REX['PRICE']+r'\s$',0), r'^'+REX['PRICE']+'\s+$') }    
    text_blocks = ('.{0,2}'.join('Thanksforridingwith'),
                    r'^TIP\s+DRIVER',2)

    def row_fix(self,row,rec_num):
        if row[COLS.index('Date')]:
            row[COLS.index('Date')] = ' '.join(row[COLS.index('Date')].split()).title()
        return 0


class LyftTip(Receipt):
    has_txt = ('LyftMail',
               re.compile(r'Tip\s+Increase\s+Receipt'))
    _counter = 0
    category = 'Car'

    parameters = { 'Account' : ((r'Charges\s+to\s',0),r'\s\*(\d{4}):'),
                    'Date' : ((r'Ride\s+with\s',0), r'\sending\s+'+REX['DATESTRYOPT']+r'\s+at\s'),
                    'Total' : ((REX['PRICE'],0), REX['PRICE']) }    
    text_blocks = (r'^Tip\s+Increase\s+Receipt',
                    r'^c\s+Lyft\s',0)

    def row_fix(self,row,rec_num):
        if row[COLS.index('Date')]: row[COLS.index('Date')] += ', ' + str(YEAR)
        return 0

 
class Uber(Receipt):
    has_txt = ('Uber',re.compile(r'Thanks\s+for\s+riding,\s'))
    _counter = 0
    category = 'Car'

    text_blocks = (None,
                    r'You\s+rode\s+with\s',0)
    
    parameters = { 'Account' : ((r'\?+\s+\d{4}\s',0),r'\?+\s+(\d{4})\s'),
                   'Date' : ((r'^Total:?\s+'+REX['PRICE'],1),REX['DATESTR']),
                   'Total' : ((r'^Total:?\s+'+REX['PRICE'],0),REX['PRICE']) }

    def row_fix(self,row,rec_num):
        if row[COLS.index('Total')]: row[COLS.index('Total')] = row[COLS.index('Total')].replace('$','')
        return 0


class UberTip(Receipt):
    has_txt = ('Uber',re.compile(r'Thanks\s+for\s+tipping,\s'))
    _counter = 0
    category = 'Car'

    text_blocks = (None,
                    r'You\s+rode\s+with\s',0)
    
    parameters = { 'Account' : ((r'\?+\s+\d{4}\s',0),r'\?+\s+(\d{4})\s'),
                   'Date' : ((r'^Total:?\s+'+REX['PRICE'],1),REX['DATESTR']),
                   'Total' : ((r'^Total:?\s+'+REX['PRICE'],0),REX['PRICE']) }


class Via(Receipt):
    has_txt = ('ridewithvia',
               re.compile(r"Here's\s+the\s+receipt\s+for\s+your\s+recent\s+trip."))
    _counter = 0
    category = 'Car'

    text_blocks = (r'Trip\s+Date',r'Please\s+note:\s+credit',0)

    parameters = { 'Account' : ((r'Charged\s+to\s',0),r'(\d{4}):\s'),
                   'Date' : ((0,0),r'^\s*'+REX['DATESTR']),
                   'Total' : ((r'Total\s+Amount\s+Billed:',1),REX['PRICE']+'\s+\$[\s\d\.,]+\s*$') }

    def row_fix(self,row,rec_num):
        if row[COLS.index('Date')]:
            row[COLS.index('Date')] = ' '.join(row[COLS.index('Date')].split())
        return 0


class ViaTip(Receipt):
    has_txt = ('ridewithvia',
               re.compile(r"Here's\s+your\s+receipt\s+for\s+the\s+tip\s+you\s+added\s+for"))
    _counter = 0
    category = 'Car'

    text_blocks = (r'The\s+Via\s+Team',r'Please\s+note:\s+credit',0)

    parameters = { 'Account' : ((r'Billed\s+To\s',0),r'(\d{4}):\s'),
                   'Date' : ((r'Trip\s+Date',0),r'\|\s+'+REX['DATESTR']),
                   'Total' : ((r'Billed\s+To\s',0),r':\s+'+REX['PRICE']+'\s+$') }

    credit_re = re.compile(r'Deducted\s+from\s+your\s+Ride\s+Credit:\s+'+REX['PRICE'])
    credit_acct = 'Cash'
    def row_fix(self,row,rec_num):
        if row[COLS.index('Date')]:
            row[COLS.index('Date')] = ' '.join(row[COLS.index('Date')].split())
        if not row[COLS.index('Total')] and not row[COLS.index('Account')]:
            for line in self.captured[rec_num]:
                credit = self.credit_re.search(line)
                if credit:
                    row[COLS.index('Total')] = credit.group(1)
                    row[COLS.index('Account')] = self.credit_acct
                    break
        return 0


class PayPalOut(Receipt):
    has_txt = (('com_servicep','paypal','ebay'),re.compile('payment\s+sent\s|sent\s+payment\s|recurring\s+sent\s',re.I))
    _counter = 0
    category = 'TBD'

    parameters = { 'Account' : ((r'Funding Source:',0),r'\s(?:x-)?(\d{4}|TXNBML)\s'),
                   'Date' : ((REX['DATESTR']+r'\sat\s',0),REX['DATESTR']+r'\sat\s'),
                   'Total' : ((r'Funding Source:',0),r'Funding Source:\s'+REX['PRICE']+'\s') }
    text_blocks = (r'^\s?Transaction details',
                   r'\sResolution\sCenter', 1)
                   
    def row_fix(self,row,rec_num):
        tot_row = COLS.index('Total')
        if not row[tot_row]: return 0
        row[tot_row] = row[tot_row][1:] if row[tot_row][0] == '-' else '-'+row[tot_row]
        if row[tot_row][0] == '-': self.category = 'Income'
        return 0


class PayPalIn(Receipt):
    has_txt = (('com_servicep','paypal','ebay'),re.compile('payment\s+received\s',re.I))
    _counter = 0
    category = 'Income'

    parameters = { 'Account' : ((0,0),REX['1CHAR']),
                   'Date' : ((r'Transaction ID:',0),REX['DATESTR']+r'\sat\s'),
                   'Total' : ((r'^Payment details',2),REX['ALL']) }
    text_blocks = (r'^\s?Transaction details',
                   r'^Need.+\?\s', 1)

    # Extract fees as seperate receipt
    withdrawl_acct = '4285'
    fee_category = 'Fees'
    no_fee = '$0.00'
    price_re = re.compile(REX['PRICE'])
    def row_fix(self,row,rec_num):
        tot_row,acct_row = COLS.index('Total'),COLS.index('Account')
        if row[acct_row] == self.withdrawl_acct: return 0
        row[acct_row] = self.withdrawl_acct
        prices = self.price_re.findall(row[tot_row])
        if not prices:
            row[tot_row] = ''
            return 0
        row[tot_row] = '-' + prices[0].replace('-','')
        new = row[:]
        new[tot_row] = prices[1].replace('-','')
        if new[tot_row] == self.no_fee: return 0
        # Get net income
        row[tot_row] = '-${:.2f}'.format(
            float(row[tot_row][1:].replace(',','').replace('$','')) -
            float(new[tot_row].replace(',','').replace('$','') ))
        new[COLS.index('Category')] = self.fee_category
        self.append_row(new)
        return 0


class VenmoOut(Receipt):
    has_txt = ('venmo','You paid ')
    _counter = 0
    category = 'TBD'
    capture_method = 'venmo_out_capture'

    parameters = { 'Account' : ((r'(Completed via\s|A total of\s)',0),r'ending in\s(\w{4})'),
                   #OLD ACCT : ((r'^A total of\s'+REX['PRICE'],0),r'ending in (\d{4}),'),
                   'Date' : ((r'\sP[SD]T\s',0),REX['DATESTR']+r'\sP[SD]T\s'),
                   'Total' : ((r'[-+]\s\$',0),r'[-+]\s'+REX['PRICE']+'\s') }
    text_blocks = (r'Transfer Date and Amount:',
                   r'Payment ID:',1)

    rec_count = -1
    fee_category = 'Fees'
    is_cash = re.compile(r'your\s*Venmo\s*balance',re.I)
    def row_fix(self,row,rec_num):
        acct_row,cat_row = COLS.index('Account'),COLS.index('Category')
        if self.rec_count > -1 and rec_num >= self.rec_count:
            row[cat_row] = self.fee_category
        if self.old_class=='VenmoIn': VenmoIn.row_fix(self, row, rec_num)
        if row[acct_row]: return 0
        for line in self.captured[rec_num]:
            if self.is_cash.search(line):
                row[acct_row] = 'Venmo'
                break
        return 0

    # Create seperate receipt for additional fees
    is_fee = re.compile(r', including a\s'+REX['PRICE']+r'\sfee, ',re.I)
    tot_re = ( re.compile(parameters['Total'][0][0]),
               parameters['Total'][0][1],
               re.compile(parameters['Total'][1]) )
    def venmo_out_capture(self, textfile):
        cap = self.capture_text_re(textfile)
        new_fees = []
        self.rec_count = len(cap)
        for rec in cap:
            fee, tot = None, 0
            for i,ln in enumerate(rec):
                if not tot and self.tot_re[0].search(ln):
                    totln = i + self.tot_re[1]
                    tot = self.tot_re[2].search(rec[totln])
                if not fee: fee = self.is_fee.search(ln)
            if fee and tot:
                new_rec = rec[:]
                new_rec[totln] = new_rec[totln].replace(tot.group(1), fee.group(1))
                new_fees.append(new_rec)
                if DEBUG['special']: print('--SPECIAL: Ceated',len(new_fees),'additional receipt(s) for fees.') 
        self.captured = cap + new_fees
        return self.captured


class VenmoIn(Receipt):
    vendor_name = 'Venmo'
    has_txt = ('venmo',' paid You')
    _counter = 0
    category = 'Income'

    backup_class = 'VenmoOut'
    regex_flags = re.I
    text_blocks = (r'^\s?Bank Transfer Initiated',
                   r'^YOUR TRANSFER NUMBER IS:|^You can see the status',0)
    parameters = { 'Account' : ((r'\s[7-~]{4}(\d{4})\s',0),r'\s[7-~]{4}(\d{4})\s'),
                   'Date' : ((r'\w{6,9},\s'+REX['DATESTRICT']+r'\s',0),r'\w{6,9},\s'+REX['DATESTRICT']+r'\s'),
                   'Total' : ((r'^TRANSFER\s*AMOUNT\s*\$|^'+REX['PRICE'],0),REX['PRICE']+'\s') }

    def row_fix(self,row,rec_num):
        if row[COLS.index('Total')]: row[COLS.index('Total')] = '-' + row[COLS.index('Total')]
        return 0

    
class Seamless(Receipt):
    has_txt = ('seamless',None)
    _counter = 0
    category = 'Meals'

    text_blocks = (r'Order\s*Details',
                   r'^\s*'+REX['PRICE']+r'\s*$',1)
    parameters = { #'Account' : ((r'',0),r''),
                   'Date' : ((r'Order\s*Details',0),r'Details\s*'+REX['DATESTRICT']),
                   'Total' : ((-1,0), r'^\s*'+REX['PRICE']+r'\s*$') }

    def row_fix(self,row,rec_num):
        row[COLS.index('Date')] = row[COLS.index('Date')].replace('\t',' ')
        return 0


class Enterprise(Receipt):
    has_txt = ('enterprise',None)
    _counter = 0
    category = 'Transportation'

    text_blocks = (r'^DATE\s*&\s*TIME\s*IN',
                   r'^CREDIT\s*CARD\s*NUMBER',1)
    parameters = { 'Account' : ((-1,0),r'x{11,13}(\d{4})'),
                   'Date' : ((1,0),r'^'+REX['DATENUM']),
                   'Total' : ((r'^TYPE\s',-2), r'\s+'+REX['PRICE']) }


class Spotify(Receipt):
    has_txt = ('spotify',None)
    _counter = 0
    category = 'Software'

    text_blocks = (r'^'+REX['DATESTR'],
                   r'^Username\s',1)
    parameters = { 'Account' : (('^Method\s',0), r'\((?:#{4}\s){3}(\d{4})\)'),
                   'Date' : ((0,0), REX['DATESTR']),
                   'Total' : ((r'^Total',1), REX['PRICE']+'\s*$') }


class Apple(Receipt):
    has_txt = ('apple',None)
    _counter = 0
    category = 'Software'

    text_blocks = (r'^DATE',
                   r'^Privacy:',0)
    parameters = { 'Account' : ((r'^BILLED\s+TO',1), r'\s+\.{4}\s+(\d{4})\s'),
                   'Date' : ((0,0),REX['DATESTR']),
                   'Total' : ((r'^TOTAL',1),REX['PRICE']) }


class QuickBooks(Receipt):
    has_txt = ('quickbooks',None)
    _counter = 0
    category = 'Software'

    text_blocks = (r'^Thank you for your order',
                   r'^Download information', 0)
    parameters = { 'Account' : ((r'\s*Payment\s*method:\s*',0), r'\s*Payment\s*method:.*\s\*(\d{4})'),
                   'Date' : ((r'\s*Order\s*date:\s*',0), r'\s*Order\s*date:\s*'+REX['DATESTR']),
                   'Total' : ((r'\s*Total\s*charges:\s*',0), r'\s*Total\s*charges:\s*'+REX['PRICE']) }

        
class SquarePay(Receipt):
    has_txt = ('square1bank',None)
    _counter = 0
    category = 'Income'

    text_blocks = (r'^DATE',
                   r'^INVOICE NUMBER',1)
    parameters = { 'Account' : ((0,0), REX['1CHAR']),
                   'Date' : ((REX['DATENUM']+r'\s+$',0),REX['DATENUM']),
                   'Total' : ((r'^AMOUNT',1),REX['PRICE']) }

    ach_acct = '4285'
    def row_fix(self,row,rec_num):
        tot_row = COLS.index('Total')
        row[COLS.index('Account')] = self.ach_acct
        row[tot_row] = '-$' + row[tot_row].replace('-','').replace('$','').strip()
        return 0



























############ SCRIPT START: DON'T MODIFY BELOW HERE ############


### Global vars w/ class dependencies
BASE_CLASS = Receipt
VENDOR_LIST = [ v for v in sys.modules[__name__].__dict__.values() if type(v) is type and BASE_CLASS in v.__bases__ ]
only_use = [ v for v in VENDOR_LIST if v.__name__ in only_use ]
if only_use == []: only_use = None
COLS += list(set( c for v in VENDOR_LIST for c in v.parameters if c not in COLS ))



### Global methods
def error(error, tabs=0, always_print=False, verbose_tabs=0):
    errstr = ''
    if VERBOSE: tabs += verbose_tabs
    if type(error) in (list,tuple):
        for e in error:
            errstr += str(e) + ' '
        errstr = errstr[:-1]
    else: errstr = str(error)
    
    current_err_log.append(errstr)
    if always_print or VERBOSE: print(('\n'+errstr).replace('\n','\n'+'\t'*(tabs))[1:])
    return None

CHR_IGNORE = (0x81,)
CHR_ASSIGNMENTS = { str([0xc2,0xa0]) : ' ', str([0xc2,0xad]) : '-', str([0xc2,0xa9]) : 'c', str([0xef,0xac]) : 'fi' }
def fix_line(in_bytes):
    # Decode byte-array to text
    # Remove any non-ASCII/UTF-8 characters from input text
    out_text,buff,new_chr,fixed = '',[],'',''
    for c in in_bytes:
        if c in CHR_IGNORE: continue
        elif c > 127:
            buff.append(c)
            if len(buff) >= 2:
                if DEBUG['badchr'] and buff not in DEBUG_IGN_CHRS: fixed+='['+hex(buff[0])+','+hex(buff[1])+'] w/ '
                if str(buff) in CHR_ASSIGNMENTS: new_chr = CHR_ASSIGNMENTS[str(buff)]
                else:
                    new_chr = buff[0]*0x10 + buff[1] - 0xc0*0x10 - 0xa0
                    #new_chr = chr( int(''.join( re.findall(r"b'\\x[c](\w)\\x[a](\w)",str(buff))[0] ), 16) ) #ALT METHOD
                    if new_chr in range(128): new_chr = chr(new_chr)
                    else: new_chr = BAD_CHR
                if DEBUG['badchr'] and buff not in DEBUG_IGN_CHRS: fixed += "'"+new_chr+"', "
                out_text += new_chr
                #if VERBOSE: print('Replaced',buff,'with',chr(new_chr)) # DEBUG LINE
                buff = []
        else: out_text += chr(c)
    if DEBUG['badchr'] and fixed:
        print('---REPLACED:',fixed[:-2])
        if not DEBUG['all']: print('--LINE:"'+out_text+'"')
    return out_text

def flip_year(date):
    # Takes format (YY)YY_MM_DD, and returns MM/DD/YY(YY)
    # From Generic parser (NOTE: Error checks for 3-places and forces use of slashes)
    sep = DATE_SEPS[0]
    for ds in DATE_SEPS[1:]:
        if ds in date:
            sep = ds
            break
    flipped = date.split(sep)
    if len(flipped) != 3: return date
    flipped.append(flipped.pop(0))
    return '/'.join(flipped)
            

def append_year(date):
    # Appends year to date (Only if needed)
    # REMOVED: not date.strip()[-1].isdigit() for '22nd' (i.e.)
    if not date.strip() \
    or any( str(y)[:3] in date for y in range(YEAR-1,YEAR+2) ):
        return date
    for sym in DATE_SEPS:
        if not sym.strip(): continue
        if sym in date:
            if date.count(sym) > 1 \
            or ( date[-3] == sym \
            and date[-2:] in (str(y)[-2:] for y in range(YEAR-1,YEAR+2)) ):
                return date
            return date + sym + str(YEAR)
    return date.strip() + ', ' + str(YEAR)







### Main methods

def parse_pdf(pdf_file):

    def get_vendor(pdf,txt):
        ocr_retry = False
        for v in VENDOR_LIST:
            ret = v.is_vendor(pdf,txt)
            if ret == 2: return v # match
            elif ret == 1: ocr_retry = True # partial match
        return False if ocr_retry else None

    def keep(f,_=None):
        is_empty = False
        if not os.path.exists(f):
            is_empty = True
            with open(f,'wb') as blank:
                pass
        elif not os.path.getsize(f): is_empty = True
            
        if VERBOSE: print('\t\t\tIncluding'+('','empty ')[is_empty]+' file')
        return int(is_empty)

    def skip(f,_=None):
        if VERBOSE: print('\t\tSkipping file, continuing process\n')
        if os.path.exists(f): os.remove(f)
        return 2

    def abort(f,_=None):        
        if VERBOSE: print('Cleaning up and aborting process\n')
        shutil.rmtree(os.path.split(f)[0])
        return -1

    def choose(f,_=None):
        # Build vendor menu
        if VERBOSE: print('\t\tManually choose vendor:')
        selection, vendors = '', [2] + VENDOR_LIST
        v = ['None'] + [ v.__name__ for v in VENDOR_LIST ]
        for n in range(len(v)//2):
            if VERBOSE: print('\t',end='')
            print('\t',str(n+1)+')',v[n],'\t',str(len(v)//2+n+1)+')',v[len(v)//2+n])
        if len(v)%2: print('\t' if VERBOSE else '','\t ',str(len(v)),') ',v[-1], sep='')
        
        while not selection.isdigit() or int(selection) not in range(1,1+len(vendors)):
            if VERBOSE: print('\t',end='')
            selection = input('\tEnter number: ').strip()

        if int(selection) == 1: return skip(f)
        return vendors[int(selection)-1]

    def ocr(out_file, in_file=None):
        ocr_log = []
        error('Re-reading PDF text',3)
        if VERBOSE: print('/-----Start pdfOCR-----')
        ret = pdf_ocr.receiptOCR(in_file,out_file,VERBOSE,ocr_log)
        if VERBOSE: print('\\-----End pdfOCR------')
        if ocr_log: current_err_log.append(';'.join(ocr_log).replace('\t','').replace('\n',','))
        if ret < 0:
            error('PDF unable to be read',2)
            os.remove(out_file)
            return keep(out_file)
        return 3

    def empty_file(in_file):
        with open(in_file, 'rb') as f:
            for ln in f:
                if ln.strip() != b'': return False
        return True

    def ask_vendor(selection, vendor):
        return selection=='K' or selection not in menu or (selection=='O' and vendor==None)

    force_ci = False
    pdf_path, p = os.path.split(pdf_file)
    pdf_path += '/'
    menu = { 'K' : keep, 'S' : skip, 'A' : abort, 'C' : choose, 'O' : ocr }
    nov_f,skip_menu,ans = p+'\n',False,0
    if VERBOSE: nov_f = ''
    
    # Make temp dir for text file
    tempdir = tempfile.mkdtemp() + '/'
    textfile = tempdir + p[:p.rfind('.')]+TXT_EXT

    # Extract text
    if VERBOSE: print('\t\tExtracting text')
    x = subprocess.run([pdftotext, pdf_path+p, textfile],
                   stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

    # No text found
    if x.stdout != b'' or empty_file(textfile):
        error('No text found', 1, AUTO=='C' or AUTO not in menu, 2)
        if x.stdout: error(x.stdout.decode(),3)
        if 'Permission Error' in x.stdout.decode():
            return (skip(textfile), Receipt(p,pdf_path))
        selection = AUTO
        while selection == 'C'  or selection not in menu:
            if VERBOSE: print('\t',end='')
            selection = input('\t[K]eep, [O]CR, [S]kip or [A]bort? ').strip()[0].upper()         
        ans = menu[selection](textfile,pdf_path+p)
        if ans < 0 or ans == 2: return (ans,Receipt(p,pdf_path))
        elif ans == 1 or ans == 3: skip_menu = True
        if OCR_FORCES_CI and ans == 3: force_ci = True

    
    ocr_retry = False
    for tries in range(2):
        # Determine vendor ID
        vendor = get_vendor(p,textfile)
        
        # Erase temp OCR textfile if it's not useful
        if tries and not vendor:
            if VERBOSE: print('\t\tCleaning up unused OCR file')
            os.rename(textfile+ORIG_POSTFIX, textfile)

        # Skip if using "only-use" mode (Still allow through if try #1)
        if only_use and vendor not in only_use:
            if vendor == None: vendor = Receipt
            elif vendor or tries:
                error('Vendor not in only_use',2)
                return (skip(textfile),vendor(p,pdf_path))

        # Auto-choose vendor
        elif ALWAYS_CHOOSE and vendor == None or (tries and not vendor):
            if ALWAYS_CHOOSE.strip().lower() == 'skip':
                error('Vendor not found',2)
                return (skip(textfile),Receipt(p,pdf_path))
            for v in VENDOR_LIST:
                if ALWAYS_CHOOSE.strip().lower() == v.__name__.lower():
                    vendor = v
                    error('Vendor not found, defaulting to '+vendor.__name__,2)
                    break
        
        # Manually choose vendor
        if not(vendor):
            if not tries: selection = AUTO
            error('Vendor not found', 1, ask_vendor(selection, vendor), 2)
            while ask_vendor(selection, vendor):
                if VERBOSE: print('\t',end='')
                selection = input('\t[C]hoose, [O]CR, [S]kip or [A]bort? ').strip()[0].upper()

            # Setup for temp OCR textfile
            if selection == 'O':
                ocr_retry = True
                os.rename(textfile, textfile+ORIG_POSTFIX)

            # Execute menu selection
            vendor = menu[selection](textfile,pdf_path+p)
            if type(vendor) is type: pass
            elif vendor < 0 or vendor == 2: return (vendor,Receipt(p,pdf_path))
            elif vendor == 3 and not tries:
                selection = AUTO.replace('O',OCR_FAIL_AUTO)
                continue # Try again after OCR
        break

    # Cleanup OCR temp file
    if os.path.exists(textfile+ORIG_POSTFIX): os.remove(textfile+ORIG_POSTFIX)
    
    # Isolate text
    if VERBOSE: print('\t\tCapturing text as',vendor.__name__.replace(BASE_CLASS.__name__,'Generic'),'receipt')
    vendorobj = vendor(p,pdf_path)
    selection = AUTO
    if force_ci:
        if VERBOSE: print('\t\tForcing case-insensitivity due to OCR pass.')
        vendorobj.regex_flags = vendorobj.regex_flags | re.I
        
    for tries in range(2):    
        vendorobj = vendorobj.capture_text(textfile)
        if isinstance(vendorobj.captured,int): return (abort(textfile),vendorobj)
        
        # No capture data found
        if not vendorobj.captured and not skip_menu:
            error('No data found', 1, AUTO=='C' or AUTO not in menu, 2)
            while selection == 'C' or selection not in menu:
                if VERBOSE: print('\t',end='')
                selection = input('\t[K]eep, [O]CR, [S]kip or [A]bort? ').strip()[0].upper()           
            ans = menu[selection](textfile,pdf_path+p)
            if ans < 0 or ans == 2: return (ans,vendorobj)
            elif ans == 3 and not tries:
                selection = AUTO.replace('O',OCR_FAIL_AUTO)
                continue
        break

    # Run captured data through vendor's default parse method
    if VERBOSE: print('\t\tParsing text')
    ans = vendorobj.parse()
    if DEBUG['rawend']: print('--OBJDATA: '+repr(vendorobj))
    if DEBUG['ending']: print('--ENDING: parse return: ',ans,' parsed.name: ', vendorobj.name,sep='')
    if ans == -1: return (abort(textfile),vendorobj)

    # Cleanup and return data
    shutil.rmtree(os.path.split(textfile)[0])
    return (ans,vendorobj)

ORIG_POSTFIX = '.orig'
def main_loop(top_dir, out_file):

    def write_log(*additional_data):
        log_file = out_file[:out_file.rfind('.')]+'_log'+CSV_EXT
        new_file(log_file)
        return csv_append(log_file, csv_format(log_format(receipts,top_dir,*additional_data)))

    def csv_format(data):
        # If it's a cell:
        if type(data) not in (list,tuple):
            data = str(data)
            if CSV_COL in data or CSV_ROW in data: data = '"'+data.replace('"',"'")+'"'
            return data
        # Return blank row
        if len(data) < 1: return ''
        # Convert 1D list into CSV row
        if type(data[0]) not in (list,tuple): return CSV_COL.join( csv_format(cell) for cell in data ) + CSV_ROW
        # Convert 2D list into CSV table
        return ''.join( csv_format(row) for row in data )

    def new_file(filepath):
        with open(filepath,'w') as f:
            f.flush()
        return 0
    
    def csv_append(filepath,data):
        with open(filepath,'a+') as csv:
            csv.write(data)
            csv.flush()
        return 0

    
    print('Parsing all PDF files in',top_dir,'\nSaving to',out_file)
    if VERBOSE: print()
    else: print('This make take some time...')

    # Init vars
    counts = [0,0,0]
    receipts = [] # Completed, Empty, Skipped
    new_file(out_file)
    csv_append(out_file,csv_format(Receipt.get_title_row()))
    
    # Path Walk Loop
    for pdf_path, subs, files in os.walk(top_dir):
        pdfs = [ f for f in files if f[-4:].lower() == '.pdf' ]
        if len(pdfs) < 1: continue

        # Folder Header
        if INCLUDE_FOLDERS: csv_append(out_file,csv_format([[''],['']*(len(COLS)+1)+['FOLDER: '+os.path.split(pdf_path)[1].title()]]))
        if VERBOSE: print('Folder:',os.path.split(pdf_path)[1])

        # Parse all files in folder
        for p in pdfs:
            if VERBOSE: print('\tFile:',p)
            pdfobj = parse_pdf(pdf_path+'/'+p)
            pdfobj[1].save_err_log()
            counts[min(2,max(-1,pdfobj[0]))] += 1
            receipts.append(pdfobj)
            if pdfobj[0] < 0:
                write_log('EXIT CODE: '+str(pdfobj[0])+' ON: '+p)
                return pdfobj[0] # Aborted
            if pdfobj[0] == 2: continue # Skipped
            if VERBOSE: print('\t\tSaving text to CSV')
            csv_append(out_file,csv_format(pdfobj[1].get_list())) # Add to CSV
            if VERBOSE: print()
    
    print('\nCompleted parsing',sum(counts),'receipts.')
    print('Output',counts[0],'normal and',counts[1],'blank receipts. Skipped',counts[2],'receipts.')
    
    save_log = LOG
    if VERBOSE and not save_log: save_log = input('Save log (y/n)? ').strip()[0].lower() == 'y'
    if save_log: write_log('EXIT CODE: 0')

    return 0

            

def main(top_dir='',vbose=False,out_file=None,year_prefix=None,auto_menu=None,def_receipt=None,make_log=False):
    global YEAR, VERBOSE, AUTO, ALWAYS_CHOOSE, LOG
    
    # Get top directory to begin sub-directory search
    folder = 'Directory: '+top_dir if VERBOSE else 'Folder' 
    while not os.path.exists(top_dir):
        if top_dir != '': print(folder+' is invalid.', end=' ')        
        top_dir = input('Enter path containing PDFs: ').strip()
    if top_dir[-1] == '/': top_dir = top_dir[:-1]
    if vbose: print('Input directory:',top_dir,end='\n\n')

    # Set output file to write to
    if out_file == None: out_file = top_dir + '/' + CSV_FILENAME + CSV_EXT
    while not os.path.exists(os.path.split(out_file)[0]) and os.path.exists(out_file):
        if out_file != '': print('File is invalid or already exists.', end=' ')        
        out_file = input('Enter filepath to save CSV: ').strip()
        if out_file[0] != '/': out_file = top_dir + '/' + out_file
        if '.' not in out_file: out_file += CSV_EXT
    if vbose: print('Output file:',top_dir,end='\n\n')

    # Get year prefix (Automatically if not near decade barrier)
    if year_prefix == None:
        year_prefix = datetime.datetime.now().year
        if (year_prefix + 1)//10 != (year_prefix - 1)//10: year_prefix = 0
    if type(year_prefix) is str and year_prefix.isdigit(): year_prefix = int(year_prefix)
    while type(year_prefix) is not int or year_prefix not in range(1900,datetime.datetime.now().year+15):
        if year_prefix != 0: print('Not a vaild year.', end=' ')        
        year_prefix = input('Enter the year on the receipts: ').strip()[:4]
        if year_prefix.isdigit(): year_prefix = int(year_prefix)
    if vbose: print('Using year prefix:',year_prefix,end='\n\n')
    YEAR = year_prefix

    # Get automatic menu answer
    entries = ('None','Keep','Skip','Abort','OCR')
    if auto_menu != None:
        if len(auto_menu) > 0: auto_menu = auto_menu.strip()[0].upper()
        while auto_menu not in (e[0] for e in entries):
            auto_menu = input('Select automatic menu entry ('+'/'.join(entries)+'): ').strip()[0].upper() 
        if auto_menu == 'N': auto_menu = None
    if vbose and auto_menu: print('Automatic choice:',entries[[e[0] for e in entries].index(auto_menu)],end='\n\n')
    AUTO = auto_menu

    # Get default receipt to use (Or none, or skip)
    receipts = ['none','skip',BASE_CLASS.__name__.lower()] + [v.__name__.lower() for v in VENDOR_LIST]
    def_receipt = def_receipt.lower()
    if AUTO not in ('S','A') and def_receipt and def_receipt not in receipts:
        print('Choose default receipt (None will ask each time):')
        for n in range(len(receipts)//2):
            print(str(n+1)+')',receipts[n].title(),'\t',
                  str(len(receipts)//2+n+1)+')',receipts[len(receipts)//2+n].title())
        if len(receipts)%2: print(str(len(receipts))+')',receipts[-1].title())
        while def_receipt not in receipts:
            def_receipt = input('Enter number: ').strip()
            if def_receipt.isdigit():
                def_receipt = int(def_receipt) - 1
                if def_receipt in range(len(receipts)): def_receipt = receipts[def_receipt]
        if not(def_receipt) or def_receipt == 'none': def_reciept = None
    if vbose and AUTO not in ('S','A'):
        def_rtext = 'ask user'
        if def_receipt == 'skip': def_rtext = 'auto-skip file'
        elif def_receipt: def_rtext = 'use ' + def_receipt.title()
        print('If no receipt found',def_rtext,'\n')
    ALWAYS_CHOOSE = def_receipt

    # State if logging is enabled
    LOG = make_log
    if vbose: print('Logging',('enabled','disabled')[not(make_log)],end='. ')
    
    # State if verbose mode is enabled
    VERBOSE = vbose
    if vbose: print('Verbose mode enabled.\n')
    
    return main_loop(top_dir, out_file)


def default(top_dir):
    # Use default parameters
    return main(top_dir,VERBOSE,None,YEAR,AUTO,ALWAYS_CHOOSE,LOG)


default(inp_dir)
    
