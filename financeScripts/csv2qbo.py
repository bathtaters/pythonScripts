"""
Convert from CSV to OFX (Importable by QuickBooks)

Dependencies:
  csv2ofx

To Run:
  Load module then use csv2qbo(input_csv, output_qbo, mapping, start_date?)
  Run on command line using: python ./csv2qbo input_csv output_qbo
  To change mapping for command line you must edit CSV MAPPING, below
"""



#### CSV Mapping ####  See csv2ofx "Mappings" for more details  ####

"""
For custom mappings:
  - To use same value for all txs = "<VALUE>"
  - To use value directly from column = itemgetter("<COLUMN HEADER>")
  - To derive value from each row = lambda row: ... (row = row as Dict using column headers)
NOTE: Required mapping keys: account, date, amount, class & desc (or notes or payee)
      It is also recommended that you set has_header(T), is_split(F) & delimiter(,)
"""

from operator import itemgetter
mapping = {
    "has_header": True,
    "is_split": False,
    "delimiter": ",",
    #"bank": "Bank",
    #"currency": "USD",
    "account": "My Account",
    "date": itemgetter("Trans. Date"),
    "amount": lambda r: r["Amount"][1:] if r["Amount"][0] == '-' else '-' + r["Amount"],
    "desc": itemgetter("Description"),
    "class": itemgetter("Category"),
    #"payee": itemgetter("Description"),
    #"notes": itemgetter("Notes"),
    #"check_num": itemgetter("Num"),
    #"id": itemgetter("Row"),
}

"""
For mapping presets check below folder (Replacing <V> with current python version):
  /path/to/python/<V>/lib/python<V>/site-packages/csv2ofx/mappings
  i.e. for MacOS: /Library/Frameworks/Python.framework/Versions/<V>/lib/...
Then uncomment below line and change 'default' to selected mapping 
"""
#from csv2ofx.mappings.default import mapping








#### Advanced Settings ####

DEF_START_DATE = '19700101'
""" Start date for transactions (Format: 'YYYYMMDD') """

def bank_id(user_data: dict) -> str:
    """
    Return Bank ID (as a string) from user_data
    - This must be a valid Intuit BID or QuickBooks won't import!
    - user_data properties: "acct_id", "acct_type", "end_bal", "end_dt"
    - See csv2qbo_BIDs.csv for full list of BANK_IDs (NOTE: Some IDs may be outdated and will not work)
    - Example: '3106' = Amex, '2102' = CitiBank
    """
    return '3106' if user_data["acct_type"] == 'CREDIT' else '2102'


# Parameters to convert csv2ofx OFX to QBO-compatable OFX

def find_repl_base(user_data, start_dt):
    """ Replace anything matching KEY (RegExp) with corresponding VALUE (String) """
    bid = bank_id(user_data)
    return {
        r'^': "OFXHEADER:100\n",
        
        "</LANGUAGE>": f'</LANGUAGE>\n\t\t\t<INTU.BID>{bid}</INTU.BID>',
        "</BANKTRANLIST>": '</BANKTRANLIST>\n\t\t\t\t<LEDGERBAL>\n\t\t\t\t\t'+
                f'<BALAMT>{user_data["end_bal"]:.2f}</BALAMT>\n\t\t\t\t\t'+
                f'<DTASOF>{user_data["end_dt"]}</DTASOF>\n\t\t\t\t'+
            '</LEDGERBAL>',

        r'<DTSTART>[^<]+<':  f'<DTSTART>{start_dt}<',
        r'<DTEND>[^<]+<':    f'<DTEND>{user_data["end_dt"]}<',    
        r'<ACCTID>[^<]*<':   f'<ACCTID>{user_data["acct_id"]}<',
        r'<ACCTTYPE>[^<]*<': f'<ACCTTYPE>{user_data["acct_type"]}<',

        r'\t+<BANKID>[^<]*</BANKID>\n': "",
    }


def find_repl_cc():
    """ Replace anything matching KEY (RegExp) with corresponding VALUE (String) for CreditCards ONLY """
    return {
        "BANKMSGSRSV1": "CREDITCARDMSGSRSV1",
        "STMTTRNRS":    "CCSTMTTRNRS",
        "STMTRS":       "CCSTMTRS",
        "BANKACCTFROM": "CCACCTFROM",

        r'\t+<ACCTTYPE>[^<]*</ACCTTYPE>\n': "",
    }


def is_cc(data):
    """Return TRUE if find_repl_cc (above) should be run"""
    return data["acct_type"] == 'CREDIT'


# Default UI values
from datetime import date, datetime
DEF_ACCT_TYPE = 0            # Index of ('CREDIT','CHECKING','SAVINGS')
DEF_END_BAL   = 0            # Float
DEF_END_DATE  = date.today() # Format datetime obj

# QBO Constants
MAX_ACCT_ID_SIZE = 22










#### Main Script ####

import re, sys, uuid
from pprint import pformat
from csv import DictReader
from csv2ofx import utils
from csv2ofx.ofx import OFX


def csv2qbo(csv_in, qbo_out, mapping, start_date=DEF_START_DATE):
    """Convert CSV of transactions to QuickBooks-compatible OFX file (AKA QBO)"""

    print('*** Convert CSV to QBO ***\n')
    user_data = get_ui(csv_in, qbo_out, mapping, start_date)
    
    print('Reading CSV...',end=' ')
    with open(csv_in, 'r') as csvfile:
        csv_txs = [ r for r in DictReader(csvfile) ]
    print('DONE')
        
    print('Converting...',end=' ')
    ofx_text = csv_to_ofx(csv_txs, mapping)
    ofx_text = replace_all(ofx_text, find_repl_base(user_data, start_date))
    if is_cc(user_data): ofx_text = replace_all(ofx_text, find_repl_cc())
    print('DONE')

    print('Saving QBO...',end=' ')
    with open(qbo_out, 'w') as outfile:
        outfile.write(ofx_text)
    print('DONE')
    
    return ofx_text



def get_ui(in_path, out_path, mapping, start_date):
    """Get user data for spreadsheet"""

    acct_type = get_pick(('CREDIT','CHECKING','SAVINGS'),'Select Account Type:',DEF_ACCT_TYPE+1)

    acct_id = input('Enter last 4 digits of account/card number (Default: UUID): ')
    if not acct_id: acct_id = str(uuid.uuid4()).replace('-','')[MAX_ACCT_ID_SIZE:]
    else: acct_id = 'XXXX' + acct_id[:MAX_ACCT_ID_SIZE - 4]

    end_dt = get_date('Enter date of final ledger balance', DEF_END_DATE).strftime('%Y%m%d')
    end_bal = get_float(f'Enter ledger balance on {end_dt} (Without $)', DEF_END_BAL)

    print(f'\nSettings:\n  Account Type: {acct_type}\n  Account ID: {acct_id}\n'+
          f'  Start Date: {start_date}\n  Ledger at {end_dt}: ${end_bal}\n'+
          f'  Input CSV: {in_path}\n  Output QBO: {out_path}\n  Mapping: {dict_str(mapping, "  ")}')
    input('Press <Enter> to Continue or <Ctrl+C> to Quit ')
    print()

    return { 'acct_type': acct_type, 'acct_id': acct_id, 'end_dt': end_dt, 'end_bal': end_bal }



def csv_to_ofx(csv_txs, mapping):
    """Convert CSV Dict to OFX string"""
    ofx = OFX(mapping)
    
    txs = ofx.gen_groups(csv_txs)
    txs = ofx.gen_trxns(txs)
    txs = ofx.clean_trxns(txs)
    data = utils.gen_data(txs)
    body = '\n'.join(ofx.gen_body(data))

    return ofx.header() + body + ofx.footer()


def replace_all(text, find_repl_dict):
    """Run replace on text for each item in Dict of { regex_pattern: replacement_text }"""
    for pattern, repl in find_repl_dict.items():
        text = re.sub(pattern, repl, text)

    return text



def get_pick(items, prompt = 'Select one:', default_1_idx = None):
    """Request user to pick an item from a list"""
    print (prompt)
    for i, item in enumerate(items):
        print(f'  {i+1}) {item}')

    item_idx = get_int('', len(items)+1, 1, default_1_idx)
    return items[item_idx - 1]



def get_date(prompt = 'Enter date', default = None):
    """Request a date from the user as MM-DD-YYYY, loop until one is given"""
    def_txt = f' (Format: MM-DD-YYYY, Default: {default})' if default else ' (Format: MM-DD-YYYY)'
    while True:
        ans = input(prompt + def_txt +': ')
        if default and not ans: return default
        try:
            dt = datetime.strptime(ans, '%m-%d-%Y').date()
            return dt
        except ValueError:
            print('  Not a date')
    

def get_int(prompt = '', upper = 0xFFFF, lower = 0, default = None):
    """Request an int in the given range from user, loop until one is given"""
    def_txt = '' if default is None else f' (Default: {default})'
    while True:
        ans = input(prompt+def_txt+': ')
        if default is not None and not ans: return default
        try:
            num = int(ans)
            if num in range(lower, upper): return num
            print(f'Must be in range {lower} - {"Infinity" if upper == 0xFFFF else upper - 1}')
        except(ValueError):
            print('  Not a number')
            

def get_float(prompt = '', default = None):
    """Request a positive or negative float from user, loop until one is given"""
    def_txt = '' if default is None else f' (Default: {default})'
    while True:
        ans = input(prompt+def_txt+': ')
        if default is not None and not ans: return default
        try:
            num = float(ans)
            return num
        except ValueError:
            print('  Not a decimal number')


def dict_str(dictionary, linestart = ''):
    """Pretty Print Dictionary"""
    out = re.sub('^{', '{\n ', pformat(dictionary))
    out = re.sub('}$', '\n}', out)
    return re.sub('\n', '\n'+linestart, out)


def get_args():
    """Get commandline arguments"""
    if len(sys.argv) < 3:
        print("Usage: csv2qbo SOURCE_CSV DESTINATION_QBO")
        sys.exit(1)

    return (sys.argv[1], sys.argv[2])



## CLI ##

if __name__ == "__main__":
    paths = get_args()
    csv2qbo(paths[0], paths[1], mapping)
