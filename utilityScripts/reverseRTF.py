# Reverse order of lines in a simple .rtf file
# 1st line stays put
# NOTE: outfile will be overwritten w/o checking

# Files
infile = "/path/to/input/file.rtf"
outfile = "/path/to/output/file.rtf"



# Method to 'swap' lines
def swapped(lines):
    # Reverse order of lines
    return lines[::-1]

# Start/Break/End IDs
sid = b'\\f0\\b '
bid = sid
eid = b'}'






# --- SCRIPT --- #

def main():
    # Initialize vars
    arr = []
    hdr,ftr = b'',None

    print('Ingesting',infile)
    with open(infile,'rb') as i:
        init = False
        buff = None
        # Read header
        for ln in i:
            if ln[:len(sid)]==sid:
                buff = ln
                break
            hdr += ln
        # Read lines
        for ln in i:
            if ln[:len(sid)]==sid:
                arr.append(buff)
                buff = b''
            elif ln[:len(eid)]==eid:
                arr.append(buff)
                ftr = ln
                break
            buff += ln
        # Read footer
        for ln in i:
            ftr += ln

    # Output to file
    print('Saving',outfile)
    with open(outfile,'wb') as o:
        o.write(hdr)
        for ln in swapped(arr):
            o.write(ln)
        o.write(ftr)

    print('Done')

main()
