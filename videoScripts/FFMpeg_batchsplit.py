# Split video based on CSV
# Requires FFMpeg
#   CSV columns: [START SECS],[DURATION],[FILENAME]
#   (Sample Column: "182.29, 72.38, 2A_02")
csv_in = '/path/to/split.csv'
header_col = False # True to ignore 1st column

# Input video 
v_in = '/path/to/input/video.mp4'
# Output directory and file extension
out_dir = '/path/to/output/folder/'
out_ext = '.mp4'

# Options to pass to FFMpeg Decoder
in_opts = ''
out_opts = '-c:v copy -c:a copy'

# Write new files (False just prints command txt)
write = False




# FFMpeg directory
ffmpeg = '/usr/bin/ffmpeg'
# NOTE: requires that ffmpeg is installed
# Only tested on FFMpeg v1








##### SCRIPT #####

import csv,subprocess,os

if write: os.makedirs(out_dir, exist_ok=True)

if out_dir[-1:]!='/': out_dir = out_dir + '/'


info = None

print('Reading CSV...',end=' ')
slist = []
try:
    slist = open(csv_in,'r').readlines()
except IOError:
    print('ERROR')
if header_col: slist = slist[1:]
info = []
for sline in slist:
    s = None
    if sline[-1]=='\n': s = -1
    info = info + [sline[:s].split(',')]

if len(info) > 0: print('DONE')


if write: print('Now converting',end=' ')
else: print('Now building',end=' ')
print(str(len(info))+' files.')
e = 1
output = []
for i in range(len(info)):
    if len(info[i]) != 3:
        e = e + 1
        result = 'Corrupted CSV entry: "'+str(info[i])+'". Length is '+str(len(info[i]))+', should be 3.'
        output = output + [result]
        print(str(i+1).zfill(2)+': '+result)
        
    else:
        if write: print('Converting',end=' ')
        else: print('Building',end=' ')
        print(str(i+1).zfill(2)+': '+info[i][2]+'...',end=' ')
        
        ap = ''
        if os.path.exists(out_dir+info[i][2]+out_ext):
            c = 1
            while os.path.exists(out_dir+info[i][2]+'_'+str(c)+out_ext):
                c = c + 1
            ap = '_'+str(c)
        
        batcmd = ffmpeg+' -ss '+info[i][0]+' '+in_opts+' -i "'+v_in+'" '+out_opts+' -t '+info[i][1]+' "'+ out_dir + info[i][2]+ap+out_ext+'"'
        if write:
            result = ''
            try:
                result = subprocess.check_output(batcmd, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as err:
                result = err.output.decode() + '\nERROR CODE: ' + str(err.returncode)
                e = e + 1
                print('ERROR')

            if type(result) is bytes:
                print('DONE')
                result = result.decode()
            output = output + [result]
        else:
            print(str(i+1).zfill(2)+': '+batcmd)


if not(write): print('\nBuilt',end=' ')
else: print('\nConverted',end=' ')
print(str(len(info)+1-e)+' out of '+str(len(info))+' files')

n = '0'
while n != '' and write:
    n = input('Enter file number or "all" to save output status, or nothing to quit: ')
    if n=='': break
    elif n.isdigit() and (int(n) > 0 and int(n) <= len(info)):
        x = int(n)-1
        print('Writing log to: '+out_dir+info[x][2]+'.log',end='... ')
        log = open(out_dir+info[x][2]+'.log', mode='w')
        log.write(str(x+1).zfill(2)+':'+info[x][2]+'\n'+output[x]+'\n')
        log.close()
        print('SAVED')
    elif 'all' in n.lower():
        print('Write '+str(len(info))+' logs...')
        os.makedirs(out_dir+'/logs/', exist_ok=True)
        for x in range(len(info)):
            print('\tWriting log to: '+out_dir+info[x][2]+'.log',end='... ')
            log = open(out_dir+'/logs/'+info[x][2]+'.log', mode='w')
            log.write(str(x+1).zfill(2)+':'+info[x][2]+'\n'+output[x]+'\n')
            log.close()
            print('SAVED')
        print('COMPLETED')
    else:
        print('ERROR: File number invalid.')
        print('INDEX:')
        for x in range(len(info)):
            print(str(x+1).zfill(2)+': '+info[x][2])
