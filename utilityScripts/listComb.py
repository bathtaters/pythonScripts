# Comb through list and merge similar entries
# Input list should have 1 item per line
# Output list will be CSV with matches combined into each row

# Path to list
inp = '/path/to/input/list.txt'
out = '/path/to/output/list.csv' # None = debug mode


# OPTIONS
TYPO_RANGE = (0,1) # (min,max) typos before it is mismatched, None skips rough matching
ACCU_TYPO = False # Use more accurate typo checking, False is faster
UPDATE = 4 # Frequency to print % updates, None skips updates
SAMPLESIZE = None # Comb first N lines of list, None combs all
USE_KEYS = None # Only save these match-types (Index(es) of KEY), None saves all

# Definition for USE_KEYS (Enter index of this array)
KEY = ('See below','Exact match', 'Partial match', 'Match with typo')














# --- ADVANCED OPTIONS --- #
ENC = 'utf-8'
DELIM, LB, QT = ',', '\n', '"'
HEADING = ('COMPANY NAME','ROW','MATCH TYPE')


# --- SCRIPT --- #

import re
from difflib import SequenceMatcher

if type(USE_KEY) is int: USE_KEY = (USE_KEY,)
def add(arr,index='',outp=None):
    if USE_KEY != None and arr[2] not in USE_KEY: return -1
    entry = (QT+arr[1].strip()+QT, str(index), KEY[arr[2]])
    if outp:
        with open(outp, 'a', encoding=ENC) as of:
            of.write(DELIM.join(entry) + LB)
    else: output.append(entry)
    return 0

def sanit(st):
    return re.sub(r'[^a-zA-Z0-9]','', st).lower()


def matches(a,b):
    if a == b: return 1 # Exact match
    if a == '' or b == '': return 0 # Empty entry

    # Trim size
    ln = min(len(a),len(b))
    at,bt = a[:ln],b[:ln]

    if at == bt: return 2 # Partial match

    if TYPO_RANGE and TYPO_RANGE != (0,0):
        seq = SequenceMatcher(None,a,b,False)
        t,s = len(a) + len(b), 0
        if ACCU_TYPO: s = seq.ratio()
        else: s = seq.quick_ratio()
        typos = round((t-(t*s))/2)
        if typos <= TYPO_RANGE[1] and typos >= TYPO_RANGE[0]:
            return 3 # Match within typos range

    return 0
        
def main(infile=inp,outfile=None):
    global output

    # Zero out shit
    if outfile:
        with open(outfile, 'w', encoding=ENC) as of:
            of.write(DELIM.join(HEADING)+LB)
    else: output = []
    
    # Open spreadsheet
    with open(infile, 'r', encoding=ENC) as f:
        ss = f.readlines()
        size = len(ss)
        if SAMPLESIZE: size = SAMPLESIZE
        print('Combing',size,'entries')

        # Main loop
        last = ('','',False)
        for i in range(size):
            co = ss[i]
            new = sanit(co)
            mch = matches(new,last[0])
            if mch and not last[2]: last = (last[0],last[1],mch) # Fix for 0 rsn
            if mch or last[2]: add(last,i,outfile)
            last = (new,co,mch)
            
            if UPDATE and i%(size//UPDATE) == 0: print('\t ',int(100*i/size),'%',sep='')
        
        if last[2]: add(last,size,outfile) # Check last item
    if UPDATE: print('\t100%')

    # Display output
    
    if not(outfile):
        print('\nNo output file\n'+'\t'.join(HEADING))
        counts = [0]*4
        for i in range(len(output)):
            counts[KEY.index(output[i][2])] = counts[KEY.index(output[i][2])] + 1
            print(*output[i],sep='\t')
        print('\nTotal:',len(output),',',KEY[1],counts[1],',',KEY[2],counts[2],',',KEY[3],counts[3])
        print('Typo Threshold:',TYPO_THRESH,', Accurate Typo Check:',ACCU_TYPO,', Update Freq:',UPDATE)
    else: print('Saved to',outfile)


main(inp,out)

