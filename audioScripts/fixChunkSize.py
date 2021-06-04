# Fixes corrupted chunk sizes in Broadcast Wave files

### CHOOSE FOLDERS
folder_to_convert = '/path/to/corrupted/files'
folder_to_save = '/path/to/save/in'
# To overwrite corrupted files, uncomment below line
#folder_to_save = folder_to_convert 

### BASIC OPTIONS
header_title = 'bext' # Name of chunk w/ wrong size
header_size_add = 1 # Add to sizeOf field in chunk




### ADVANCED OPTIONS
header_size_byte_len = 4 # Number of bytes in header size (4 for BWV)
header_size_endianess = 'little' # 'big' or 'little' (Little for BWV)
start_byte = 0 # Start byte for header search
header_end_byte = 10212 # End byte for header search (-1 = end of file)
folder_slash = '/'
copy_protocol = "/usr/bin/rsync --archive"














import os, shlex, subprocess
if folder_to_convert[-1:]!=folder_slash: folder_to_convert = folder_to_convert + folder_slash
if folder_to_save[-1:]!=folder_slash : folder_to_save = folder_to_save + folder_slash

# Test if file exists
def exists(file):
    try:
        with open(file) as f: pass
    except IOError as e:
        return os.path.isdir(file)
    return True

# Create new folder
def newdir(path):
    if not(exists(path)):
        os.mkdir(path)
        return True
    return False

# Build file list
def getfilelist(folder):
    files = os.listdir(folder)
    for i in range(len(files),0,-1): # Remove hidden files, in reverse iterations
        if '.' == files[i-1][:1]: files.pop(i-1)
    return files

# Built from dit_rsync.py by Nick
def copy(source, destination): 
    protocol = copy_protocol
    sourcesh = shlex.quote(source)
    destinationsh = shlex.quote(destination)

    if not exists(source): return 'Source not found'
    if exists(destination):
        inp='x'
        while inp[:1]!='C':
            inp = input('Destination exists. (C)ontinue or (A)bort? ').upper()
            if inp[:1]=='A': return 'Manually terminated'
    
    

    cmd = protocol + " " + sourcesh + " " + destinationsh
    subprocess.call(cmd,shell=True)
    
    return 'Completed'

# Copy files to new location, if same location don't copy
def copyfiles(in_folder,files,out_folder):
    if in_folder == out_folder:
        input('No backups created. <Enter> to continue...')
        return
    total = len(files)
    i = 0

    for f in files:
        print('Copying file '+str(i+1)+' of '+str(total)+' ('+f+')...')
        print(copy(in_folder+f,out_folder+f))
        i = i + 1
        
# Find word position in file [repairheader]
def getposition(word,file):
    # Get sizes
    ln = len(word)
    filesize = header_end_byte
    if filesize < 0: filesize = file.seek(0,2)

    # Encode word as bytes
    w = word[0].encode(encoding='UTF-8')
    word = word.encode(encoding='UTF-8')

    # Set starting byte
    file.seek(max(start_byte,0),0)

    # Locate first letter of word, test if is word until word found
    while file.tell() < (filesize-ln):
        buff = file.read(1)
        if buff==w:
            buff = buff + file.read(ln-1)
            if buff==word: return file.tell() #return position
            file.seek(1-ln,1)
    return -1 # If not found

# Convert header length to int [repairheader]
def getheaderlen(position,file):
    file.seek(position,0)
    raw_int = file.read(header_size_byte_len)
    return int.from_bytes(raw_int,header_size_endianess)

# Overwrites header size bytes with new size [repairheader]
def overwritesize(position,new_size,file):
    file.seek(position,0)
    file.write(new_size.to_bytes(header_size_byte_len,header_size_endianess))

# Repairs header size error
def repairheader(file):    
    size_pos = getposition(header_title,file)
    if size_pos==-1: return False
    header_size = getheaderlen(size_pos,file) + header_size_add   
    overwritesize(size_pos,header_size,file)
    return True

def main():
    files = getfilelist(folder_to_convert)
    newdir(folder_to_save)
    print(str(len(files))+' files to correct.')

    i = 0

    copyfiles(folder_to_convert,files,folder_to_save)
    
    for filename in files:
        print('Repairing file '+str(i+1)+' '+filename,end='... ')
        file = ''
        
        if exists(folder_to_save+filename):
            file = open(folder_to_save+filename, mode='r+b', buffering=4096)
            if repairheader(file): print('DONE')
            else: print(header_title+' header not found')
            file.close()
            
        else: print('File not found')
        
        i = i + 1
        

main()
