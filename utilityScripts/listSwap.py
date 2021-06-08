# Swap lines in text file based on instructions file

# Main list, one item per line
masterlist = '/path/to/list.txt'

# Change instructions, each line has [Old item],[New item]
changes = '/path/to/list_instructions.csv'

# Ex. Main List has line 'test line'
#     List Instructions has line 'test line,swapped line'
#     Lines in Main List that say 'test line' will become 'swapped line'








# --- ADVANCED OPTIONS --- #
VERBOSE = True
ENC = 'utf-8'
TEMP_FILE_PREFIX = '.TEMP_'










# --- SCRIPT --- #

import os,csv
s,l = 0, 0
templist = os.path.split(masterlist)
templist = os.path.join(templist[0], TEMP_FILE_PREFIX+templist[1])

print('Swapping lines out...')
if VERBOSE: print()
swaps = [[],[]]
with open(changes, encoding=ENC) as swapfile:
    swapcsv = csv.reader(swapfile)
    for swap in swapcsv:
        swaps[0].append(swap[0].lower())
        swaps[1].append(swap[1])
        
with open(templist, mode='w', encoding=ENC) as outfile:
    with open(masterlist, encoding=ENC) as infile:
        for line in infile:
            l += 1
            if line.strip().lower() in swaps[0]:
                i = swaps[0].index(line.strip().lower())
                if VERBOSE: print('OLD:',line.strip(),'NEW:',swaps[1][i])
                s += 1
                line = swaps[1][i] + '\n'
            outfile.write(line)

os.remove(masterlist)
os.rename(templist,masterlist)
if VERBOSE and s > 0: print()
print('Completed',s,'swaps out of',l,'lines.',len(swaps[0])-s,'swaps not found.')
