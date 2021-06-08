# Parse data from a text file into a CSV table using RegEx
#   - Set file input/output
#   - Follow instructions in REG-EX PARAMETERS

# Files
infile = '/path/to/input/file.txt'
outfile = '/path/to/output/file.csv' # None = don't output



# --- REG-EX PARAMETERS --- #
#   NOTE: All reg-exes are applied on a line-by-line basis
import re

# Capture Block parameters
#   Will only capture inside these boundaries ('None' will capture from/to start/end of file)
re_capture_start = re.compile(r'[\s+$') # Start of block to search w/in (None = search whole doc)
re_capture_stop = re.compile(r'^];') # End of block to search w/in (None = search whole doc)

# Row parameters
#   Boundaries that define a single row in 'outfile'
#   NOTE: Capture group 1 of re_row_start will be saved under column TITLE_HEADER
re_row_start = re.compile(r'\sTitle: (.+),?\s+$') # Start of new row (w/ Row Title)
re_row_end = re.compile(r'}(,{)?$') # End of new row
TITLE_HEADER = "Title" # Name of column for entry title

# Column parameters (Only matches while inside Row parameters)
#   If a line matches column_re_template[0]+column_header+column_re_template[1],
#       then save capture group 1 under data_header column for the current row,
#       else line is appended under OTHER_COL_HDR column.
column_headers = ["Value","Position"] # Column headings to find
column_re_template = (r'\s',r': (.+),?\s+$') # Prefix/Postfix to make Column heading a reg-ex
OTHER_COL_HDR = "Other" # Name of column for remaining data (Not matching column heading)


# More info:

"""
# These parameters:

re_capture_start = re.compile(r'[\s+$')
re_capture_stop = re.compile(r'^];')

re_row_start = re.compile(r'\sTitle: (.+),?\s+$')
re_row_end = re.compile(r'}(,{)?$')

column_headers = ["Value","Position"]
column_re_template = (r'\s',r': (.+),?\s+$')


# Will turn <infile.txt>:

var info = [
    {
        Title: "Entry 1",
        Value: 10,
        Position: (2, 3)
    },{
        Title: "Entry 2",
        Extra: "Data",
        Value: 25,
        Position: (5, 1),
        More: "Second"
    }
];


# Into <outfile.csv>:

Title,     Value, Position, Other
"Entry 1",    10,   (2, 3),
"Entry 2",    25,   (5, 1), Extra: "Data"; More: "Second

"""













# --- ADVANCED OPTIONS --- #

# DEBUG
print_all = None # Use to print extra info for a specific Entry.name (ie. print_all = 'entry name')

# CSV SETTINGS
COL = ','
ROW = '\n'
LINE_SEP = '; ' # Seperates additional text for outputting "other"






# --- SCRIPT --- #

# Build dict
re_data = {}
re_data.update([
    (item,re.compile(column_re_template[0]+item+column_re_template[1])) for item in column_headers ])


# Object for a single entry
CSV_TITLE = TITLE_HEADER+COL+COL.join(re_data.keys())+COL+OTHER_COL_HDR+ROW
class Entry:
    def get_other(self):
        return LINE_SEP.join( line.replace(LINE_SEP,' ') for line in self.other )
        
    def csv_line(self):
        csv = '"'+self.name+'"'
        for key in re_data.keys():
            csv += COL+'"'+self.data.get(key,'')+'"'
        csv += COL+'"'+self.get_other().replace('"',' ')+'"'+ROW
        return csv
    
    def __str__(self):
        string = self.name
        for key,value in self.data.items():
            string += '\n\t'+key+': '+value
        if len(self.other) > 0: string += '\n\t'+OTHER_COL_HDR+': ['+str(len(self.other))+' lines]'
        return string
    
    def __init__(self, name):
        self.name = name
        self.data = {}
        self.other = []



# Read in file
entries = []
with open(infile, 'r', 1) as f:
    buff = None
    in_comment = not(re_capture_start)
    for line in f:
        if in_comment:
            if print_all and ((buff and buff.name == print_all) or print_all in line):
                print(' d:line:',line.strip())
            if re_capture_stop and re_capture_stop.search(line):
                if buff:
                    if print_all and buff.name == print_all:
                        print(' d:BLOCK END; SAVING ENTRY',len(entries),'\n',buff)
                    entries.append(buff)
                    buff = None
                in_comment = False
            elif re_row_start.search(line):
                if buff:
                    if print_all and buff.name == print_all:
                        print(' d:NEW ENTRY; SAVING ENTRY',len(entries),'\n',buff)
                    entries.append(buff)
                buff = Entry(re_row_start.search(line).group(1))
                if print_all and buff.name == print_all:
                    print(' d:NEW ENTRY:',re_row_start.search(line).group(1))
            elif buff:
                if re_row_end.search(line):
                    if print_all and buff.name == print_all:
                        print(' d:ENTRY END; SAVING ENTRY',len(entries),'\n',buff)
                    entries.append(buff)
                    buff = None
                    continue
                for name, re_test in re_data.items():
                    if re_test.search(line):
                        if re_test.search(line).group(1).strip() != '':
                            buff.data.update(((name,re_test.search(line).group(1)),))
                            if print_all and buff.name == print_all:
                                print(' d:ADDING VALUE OF',name,'=',buff.data[name])
                        break
                else:
                    if line.strip() != '':
                        if print_all and buff.name == print_all: print(' d:ADDING TO OTHER')
                        buff.other.append(line.strip())
        elif re_capture_start and re_capture_start.search(line): in_comment = True
    if print_all and buff and buff.name == print_all:
        print(' d:FILE END; SAVING ENTRY',len(entries),'\n',buff)
    if buff: entries.append(buff)
    
print('Found',len(entries),'entries')


# Save outfile
if outfile:
    with open(outfile, 'w', 1) as f:
        f.write(CSV_TITLE)
        for e in entries:
            f.write(e.csv_line())
    print('Saved as CSV:',outfile)
