# Clear metadata from Broadcast Wave file header
# Clears bext and iXML data without removing tags
# Thus files remain the same size
# Note: Will not search beneath 'data' chunk to save time

# Directory to work in
d = '/path/to/folder'

# Warning, changing to True will overwrite all BWF meta-data in directory
active = False












import os

if d[-1:] != '/': d = d + '/'

# User defined file list
#dirList = ['file01.wav','file02.wav']

# Build file list
dirList = os.listdir(d)

if '.DS_Store' in dirList: dirList.pop(dirList.index('.DS_Store'))


# Don't change these
bextTag = b"bext"
bextBlank = b"\x00"
xmlTag = b"iXML"
xmlBlank = b"\x20"
fmtTag = b"fmt "
wavTag = b"RIF"
dataTag = b"data"


for fn in dirList:
    buff,wav,temp = None, None, None
    if not(os.path.isdir(d+fn)):
        print('Opening '+fn,end='')
        wav = open(d+fn, 'rb')
        if wav.read(3)==wavTag: buff=b"Valid"        

    if buff==b"Valid":        
        # Format
        wav.seek(0,0)
        while buff!=fmtTag and buff!=dataTag:
            buff = wav.read(1)
            if buff[0]==fmtTag[0] or buff[0]==dataTag[0]:
                buff = buff + wav.read(3)
                wav.seek(-3,1)
        temp = wav.tell()
        wav.close()

    if buff!=dataTag:
        wav = open(d+fn, 'r+b')
        wav.seek(temp+9,0)
        chan = str(int.from_bytes(wav.read(2), 'little'))
        samp = str(round(int.from_bytes(wav.read(4), 'little')/1000,3))
        wav.seek(6,1)
        bit = str(int.from_bytes(wav.read(2), 'little'))
        s = 's'
        if chan==1: s = ''
        print(' ('+samp+'kHz '+bit+'-bit '+chan+' channel'+s+')')
        
        # Bext
        wav.seek(0,0)
        while buff!=bextTag and buff!=dataTag:
            buff = wav.read(1)
            if buff[0]==bextTag[0] or buff[0]==dataTag[0]:
                buff = buff + wav.read(3)
                wav.seek(-3,1)
        wav.seek(3,1)
        if buff!=dataTag:
            bextSize = int.from_bytes(wav.read(4), 'little')
            c = 0
            for i in range(bextSize):
                buff = wav.read(1)
                wav.seek(-1,1)
                if active and buff!=bextBlank:
                    wav.write(bextBlank)
                    c=c+1
                else: wav.seek(1,1)
            print('\tCleared '+str(c)+' bytes of bext header.')
        else:
            print('\tNo bext header found.')
        wav.close()

        # iXml
        wav = open(d+fn, 'r+b')
        while buff!=xmlTag and buff!=dataTag:
            buff = wav.read(1)
            if buff[0]==xmlTag[0] or buff[0]==dataTag[0]:
                buff = buff + wav.read(3)
                wav.seek(-3,1)
        wav.seek(3,1)
        if buff!=dataTag:
            xmlSize = int.from_bytes(wav.read(4), 'little')
            c = 0
            for i in range(xmlSize):
                buff = wav.read(1)
                wav.seek(-1,1)
                if active and buff!=xmlBlank:
                    wav.write(xmlBlank)
                    c=c+1
                else: wav.seek(1,1)
            print('\tCleared '+str(c)+' bytes of iXML header.')
        else:
            print('\tNo iXML header found.')
        wav.close()
    
    elif wav != None:
        print(' (Not a valid Broadcast Wave file).')
        wav.close()    
