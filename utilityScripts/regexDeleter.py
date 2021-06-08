# Delete all files that match a reg-ex
#   Searches recursively into subdirectories matching filenames

# Parent folder (NOTE: Searched recursively starting here)
parent_folder = "/path/to/parent/folder/"
# Filename to delete (NOTE: Matches based on reg-ex)
name_regex = r'^file\..+$'

MATCH_CASE = False # Match case
TEST_MODE = True # Don't really delete
VERBOSE = False # Print more info







# --- SCRIPT --- #

import re, os
flags = 0 if MATCH_CASE else re.I

def main(regex_exp,base_dir,regex_flags=0):
    print('Removing all files matching "'+regex_exp+'" from',base_dir)
    
    # Path walking
    match_re = re.compile(regex_exp, regex_flags)
    count,total = 0,0
    for rpath, subs, files in os.walk(base_dir):
        # Skip if no <ext> files
        rmvs = [ f for f in files if match_re.search(f) ]
        if len(rmvs) < 1: continue
        total += len(rmvs)

        # Parse all files in folder
        if VERBOSE: print('---- FOLDER:',os.path.split(rpath)[1],'----')
        for r in rmvs:
            delpath = os.path.join(rpath,r)
            if VERBOSE: print('  FILE:',r,end=' ')
            if TEST_MODE:
                if VERBOSE: print('... would be deleted.')
                else: print('TO DELETE:',delpath)
            else:
                try:
                    os.remove(delpath)
                except:
                    print('ERROR deleting',delpath)
                    continue
                if VERBOSE: print('... Deleted.')
            count += 1

    print('Done:',count,'of',total,'file(s)','matched.' if TEST_MODE else 'deleted.')
    return

main(name_regex,parent_folder,flags)
