# Append WAV header to raw audio data
# File(s) should be binary audio data (ie. data chunk from WAV file)
# File(s) cannot contain metadata or other chunks
# NOTE: Floating point may not work correctly

# Base dir of audio files (NOTE: Recurses into subdirectories)
base_dir = '/path/to/audio/data/'
ext = 'bin' # Extension of raw data files

# Metadata
samples = 44100
bitrate = 32
channels = 1
wavetype = 3 # 1 = PCM ;  3 = Floating Point
lttlendn = True # True = little-endian ; False = big-endian

# Options
DELETE_ORIGINAL = True # Delete original files
VERBOSE = False # Print all output















import os

# Header Data dict
hdr_data = {
    'rootID': 'RIFF' if lttlendn else 'RIFX',
    'fileID' : 'WAVE',
    'fmtID' : 'fmt ',
    'factID' : 'fact',
    'dataID' : 'data',
    'fmtCode' : wavetype,
    'chanCount' : channels,
    'sampRate' : samples,
    'bitRate' : bitrate,
    'fileSize' : -1
}

# Header constants
CKHDR_LEN = 8
ROOT_SIZE = 4
FMT_SIZE = 16
FACT_SIZE = 4

# Extensions
if ext[0] in (os.extsep,'.'): ext = ext[1:]
WAV_EXT = 'wav'



# Build header array using [(value, bytelen),...]
def build_hdr(data,filesize):
    
    def hdr_size(data, filesize):
        metasize = ROOT_SIZE + CKHDR_LEN + FMT_SIZE + CKHDR_LEN
        if data['fmtCode'] != 1: metasize += CKHDR_LEN + FACT_SIZE
        return metasize + filesize
        
    hdr = []

    # Root chunk
    hdr.append((data['rootID'],4))
    hdr.append((hdr_size(data,filesize),4))
    hdr.append((data['fileID'],4))

    # Format chunk
    blk_algn = data['chanCount'] * (data['bitRate'] >> 3)
    avg_bps = blk_algn * data['sampRate']
    hdr.append((data['fmtID'],4))
    hdr.append((FMT_SIZE,4))
    hdr.append((data['fmtCode'],2))
    hdr.append((data['chanCount'],2))
    hdr.append((data['sampRate'],4))
    hdr.append((avg_bps,4))
    hdr.append((blk_algn,2))
    hdr.append((data['bitRate'],2))

    # Fact chunk
    if data['fmtCode'] != 1:
        samp_count = filesize // blk_algn
        hdr.append((data['factID'],4))
        hdr.append((FACT_SIZE,4))
        hdr.append((samp_count,4))

    # Data chunk
    hdr.append((data['dataID'],4))
    hdr.append((filesize,4))

    return hdr

# Convert entry from hdr array to bytes
PADCHR = ' ' # Character to pad strings that are too short
STR_FORCE_BIGNDN = True # Strings are always Big-endian
def entry_to_bytes(entry,lndn=True):
    if type(entry[0]) is int:
        return entry[0].to_bytes(entry[1], 'little' if lndn else 'big')
    elif type(entry[0]) is str:
        word = entry[0][:4].ljust(entry[1],PADCHR)
        if len(entry[0]) != entry[1]: # WARNING
            print('\tWARNING: Entry length mismatch.',entry,'corrected to',(word,entry[1]))
        if not STR_FORCE_BIGNDN and lndn: word = word[::-1]
        return word.encode()

PERC = 10
BUFF = 4096
def convert_file(data,infile,outfile):
    filesize = os.path.getsize(infile)
    if VERBOSE: print('\tWriting header.')
    hdr = build_hdr(data,filesize)
    with open(outfile,'wb',BUFF) as f:
        for entry in hdr:
            f.write(entry_to_bytes(entry))
        f.flush()
        if VERBOSE:
            print('\tCopying data',end='')
            x, updt = 0, filesize // 10
        with open(infile,'rb',BUFF) as raw:
            for i in range(filesize//BUFF):
                f.write(raw.read(BUFF))
                if VERBOSE:
                    while x < raw.tell():
                        x += updt
                        print('.',end='')
            f.write(raw.read(filesize-raw.tell()))
    if VERBOSE: print('.')
    return 0
                
def mainloop(hdr_data,ext,base_dir):
    print('Converting all ".'+ext+'" files to ".'+WAV_EXT+'" files under',base_dir)
    
    # Path walking
    count, err = 0, 0
    for rawpath, subs, files in os.walk(base_dir):
        # Skip if no <ext> files
        raws = [ f for f in files if f[-4:].lower() == os.extsep+ext.lower() ]
        if len(raws) < 1: continue

        # Parse all files in folder
        if VERBOSE: print('---- FOLDER:',os.path.split(rawpath)[1],'----')
        for r in raws:
            if VERBOSE: print(' FILE:',r)
            inpath = os.path.join(rawpath,r)
            outpath = os.path.splitext(inpath)[0] + os.extsep+WAV_EXT
            rcode = convert_file(hdr_data,inpath,outpath)
            if rcode < 0:
                print('\tFATAL ERROR: '+str(rcode)+' ON: '+r)
                return -1 # Aborted
            elif rcode > 0:
                print('\tERROR: '+str(rcode)+' ON: '+r)
                err += 1
                continue
            if DELETE_ORIGINAL: os.remove(inpath)
            count += 1

    print('Conversion complete.',count,'file(s) saved and',err,'error(s).')
    return

mainloop(hdr_data,ext,base_dir)
