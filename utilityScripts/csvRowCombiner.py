# Combine every N lines in a CSV

# Files
in_path  = '/path/to/input.csv'
out_path = in_path.replace('.csv','-fix.csv') # Will be overwritten w/o prompt

# Number of CSV rows to combine into a single row
pattern_len = 3




## -- ADVANCED OPTIONS -- ##
import re

# Ignore these lines
exclude = re.compile(r'IGNORE TEXT') # None = ignore this rule
count_excluded = True                # Don't count excluded lines

# Force breaks at these lines (Doesn't reset normal counter)
include = re.compile(r'FORCE BREAK') # None = ignore this rule


# Method to modify last lines (Nth lines)
def fix_last(line):
    return line.strip()+'\n'

# Method to modify other lines (Non-Nth lines)
def fix_others(line):
    return line.strip()+','







## -- SCRIPT -- ##

def main(in_path,out_path,pattern_len):
    print('Opening/Combining every',pattern_len,'lines.')
    with open(out_path,mode='w') as outfile:
        with open(in_path,mode='r',encoding='utf-8') as infile:
            new,ecount = '',0
            for n,line in enumerate(infile):

                if exclude and exclude.search(line):
                    if count_excluded: ecount += 1
                    continue
                    
                if (n + 1 - ecount) % pattern_len == 0 \
                or (include and include.search(line)):
                    #print('next:')
                    #print(' new='+new)
                    #print(' line='+line,'fixed='+fix_last(line),end='')
                    outfile.write(new+fix_last(line))
                    new = ''
                    
                else: new += fix_others(line)
                
            if new:
                    #print('next:')
                    #print(' new='+new)
                    #print(' -[ END ]- ')
                    outfile.write(new)


main(in_path,out_path,pattern_len)
