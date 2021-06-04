# Print basic audio info extracted from WAV file headers

in_dir = '/path/to/wavs/'

# Give up search after...
max_bytes = 2048

# Column headers (These are just names, and have no bearing otherwise)
header = ['FILE','BITDEPT','SAMPRATE','CHANNELS']
# Filter columns based on these values ('' = print all)
only_print = ['','','',''] # Only print if column matches this value








import os

# Remove all non-WAV files
files = os.listdir(in_dir)
for i in range(len(files)-1,-1,-1):
    if not('.wav' in files[i]): files.pop(i)


# return position of word in a file (assumed mode='rb')
def wordpos(word,file):
    ln = len(word)
    w = word[0].encode(encoding='UTF-8')
    word = word.encode(encoding='UTF-8')
    file.seek(0,2)
    stop_loop = min(file.tell(),max_bytes)
    file.seek(0,0)
    i = 0
    while file.tell() < stop_loop:
        file.seek(i,0)
        buff = file.read(1)
        if buff==w:
            buff = buff + file.read(ln-1)
            if buff==word: return i
        i = i + 1
    return -1

# convert byte number to string
def getnum(byte_data):
    return str(int.from_bytes(byte_data, 'little'))


# file header
filelist = [header]
print('Parsing '+str(len(files))+' files...')
for fn in files:
    f = open(in_dir+fn,mode='rb')
    z = wordpos('fmt',f) # Find start of Format Chunk
    if z >= 0:
        f.seek(z+22,0) # bit depth = 12 + 22
        bits = getnum(f.read(2))
        f.seek(z+12,0) # sample rate = 12 + 12
        sr = getnum(f.read(4))
        f.seek(z+10,0) # channel count = 12 + 10
        chan = getnum(f.read(2))
        filelist = filelist + [[fn[:7],bits+'-bit',sr+' Hz',chan.zfill(2)]]
    else: filelist = filelist + [[fn,'--Invalid format--']] # If no format chunk
    f.close()

print()
# Output list
for wav in filelist:
    row = ''
    for a in range(len(wav)):
        row = row + wav[a] + '\t'
        if only_print[a]!='' and wav[a]!=only_print[a] and wav[a]!=header[a]:
            row = ''
            break
    if row != '': print(row)
