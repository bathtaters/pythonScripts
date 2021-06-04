# Simple FFMpeg batch script
# NOTE: requires that ffmpeg is installed

# Input/Output Directories (End with '/')
# Will attempt to convert all files within 'in_dir'
in_dir = '/path/to/input/folder/'
out_dir = '/path/to/output/folder/'

# Input/Output options (See FFMpeg documentation for info on these)
in_opts = ''
out_opts = '-c:v copy -c:a copy'

# New file extension (Will have same filename)
new_ext = '.mp4'

# Demo mode: Print terminal commands only (No execution)
demo = True




# FFMpeg location
ffmpeg = '/usr/bin/ffmpeg'




import os

if not demo: os.makedirs(out_dir, exist_ok=True)
files = os.listdir(in_dir)

print('Now converting '+str(len(files))+' files.')
i = 1
for file in files:
    print('Converting '+str(i)+' '+file+'...',end=' ')
    
    b = 4
    for a in range(len(file),0):
        if file[a]=='.':
            b = a
    ext = file[-b:]
    file = file[:-b]

    ap = ''
    if os.path.exists(out_dir+file+new_ext):
        c = 1
        while os.path.exists(out_dir+file+'_'+str(c)+new_ext):
            c = c + 1
        ap = '_'+str(c)

    cmd = ffmpeg+' '+in_opts+' -i "'+in_dir+file+ext+'" '+out_opts+' "'+out_dir+file+ap+new_ext+'"'
    if demo: print('Not Executed (Demo Mode)\n'+cmd)
    else:
        stats = os.system(cmd)
        if stats==0: print('Done')
        else: print('Error')
    i = i + 1
