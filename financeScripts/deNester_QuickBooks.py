# Flatten Quickbooks' image archive
#

# Base directory
parent = '/path/to/image/archive/'

# Settings
REMOVE_EMPTY = True # Remove empty folders
TEST_MODE = False # Won't move/copy files
COPY_MODE = False # Copy instead of move
UNLOCK = True # Attempt to unlock files on Mac (For QuickBooks Library)

# Get feedback on...
SUCCESS = False
ERROR = True
NON_FOLDER = True
EMPTY_FOLDER = True

# Advanced
MAX_DUPES = 100 # Give up if a file has this many duplicates
SKIP = ('.DS_Store',) # Ignore these files







import os, shutil

IMMUT = 2 # Unlock constant

def clear_fold(fold):
    return shutil.rmtree(fold)
    # UNUSED vvvv
    if fold[-1] != '/': fold = fold + '/'
    for f in os.listdir(fold):
        os.remove(fold+f)
    os.rmdir(fold)
    return 0

def unlock_file(file):
    flags = os.stat(file).st_flags
    if flags & IMMUT: os.chflags(file,flags ^ IMMUT)
    return 0

def main(parent):
    if parent[-1] != '/': parent = parent + '/'
    
    dlist = os.listdir(parent)
    for x in range(1,1+len(dlist)):
        if dlist[-x] in SKIP: dlist.pop(-x)

    print('De-nesting',len(dlist),'items in',parent)
    if TEST_MODE: print('NOTE: This is test mode. No writes will be committed.')
    succ,files,bad,empty = 0,0,0,0

    for f in dlist:
        if not(os.path.isdir(parent+f)) or os.path.islink(parent+f):
            if NON_FOLDER: print('\tSKIPPED: Non-folder',f)
            files = files + 1
            continue
        new = os.listdir(parent+f)
        for x in range(1,1+len(new)):
            if new[-x] in SKIP: new.pop(-x)
        
        if len(new) < 1 and REMOVE_EMPTY and not COPY_MODE:
            if not TEST_MODE: clear_fold(parent+f)
            if EMPTY_FOLDER: print('\tSKIPPED: No file, but removed empty folder',f)
            empty = empty + 1
            continue
        elif len(new) != 1:
            if ERROR: print('\tSKIPPED: Wrong file count ('+str(len(new))+')',f)
            bad = bad + 1
            continue
        
        df,c = new[0],0
        spl = df.rfind('.')
        while os.path.exists(parent+df):
            c = c + 1
            df = new[0][:spl] + '_' + str(c).zfill(2) + new[0][spl:]
            if c > MAX_DUPES: break
        if c > MAX_DUPES:
            if ERROR: print('\tSKIPPED: Too many duplicates in parent', new[0],'in',f)
            bad = bad + 1
            continue
        if SUCCESS: print('\tDENESTED:',new[0],'from',f)
        if not TEST_MODE:
            if COPY_MODE: shutil.copyfile(parent+f+'/'+new[0],parent+df)
            else:
                if UNLOCK: unlock_file(parent+f+'/'+new[0])
                shutil.move(parent+f+'/'+new[0],parent+df)
                clear_fold(parent+f)
            succ = succ + 1

    print('De-nesting completed.')
    print('\tFiles de-nested:',succ)
    if REMOVE_EMPTY and not COPY_MODE: print('\tEmpty folders removed:',empty)
    print('\tNon-folders skipped:',files)
    print('\tSkipped due to error:',bad)
    print('\nDONE')

    return succ+empty+files+bad

result = main(parent)
