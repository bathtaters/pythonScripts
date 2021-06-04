################# DIT BACKUP HELPER ####################
#                   By Bathtaters                      #
# Copy camera media to backup drive w/ integrity check #
#                                                      #
# Instructions:                                        #
#   - Edit settings below                              #
#   - Run (Recommended to run in IDLE)                 #
#                                                      #
########################################################


# Input Settings...
project = 'Project Name'
media   = 'CAM_CARD'    # Camera drive name
drive01 = 'BKUP DRIVE'  # Can include subdirectory 
drive02 =  None         # None if not using 2nd drive

# Auto-Label Options....
manual    = True    # Always ask for card#, day# & date
yesterday = False   # Use prior date in auto-label
overnight = False   # Use prior date if early in morning
multi_cam = False   # Ask for Cam letter

# Additional Options...
checkit       = True    # Integrity-check file
comprehensive = False   # Use SHA checksum vs. filesize
test_run      = False   # Don't write, output command only



# Advanced Options...
AM_CUT = 5  # Cutoff hour for normal day (24-hour)
PM_CUT = 12 # Cutoff hour for overnight day (24-hour)
diskroot = '/Volumes/' # Mount-point for disks
















##### DEPENDENCIES #####

copycmd = '/usr/bin/rsync --archive'
import subprocess, hashlib, os, shlex, threading, time, datetime



##### SCRIPT #####

def existf(file):
    try:
        with open(file) as f: pass
    except IOError as e:
        return os.path.isdir(file)
    return True

def getnames(path,delim='/'):
    s = 0
    for i in range(len(path)-1,0,-1):
        s = i
        if path[i]==delim: break
    return path[:s+1],path[s+1:]

def findtempf(orig):
    dr,fileo = getnames(orig)
    
    dirlist = os.listdir(dr)
    files = [x for x in dirlist if x[:1]=='.']
    
    for f in files:
        if fileo in f: return f

    return 'None'

def getsize(path='.'):
    size = 0
    if not os.path.isdir(path) and existf(path):
        size = size + os.path.getsize(path)
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            size = size + os.path.getsize(fp)
    return size

def size(bys):
    cross = 950
    
    suffix = ' Bs'
    div = 1
    if bys > div*cross:
        suffix = 'kBs'
        div = div*1000
    if bys > div*cross:
        suffix = 'MBs'
        div = div*1000
    if bys > div*cross:
        suffix = 'GBs'
        div = div*1000
    """if bys > div*cross:
        suffix = 'TBs'
        div = div*1000"""
    num = str(round(bys/div*100)).zfill(5)
    return num[:-2] + '.' + num[-2:] + ' ' + suffix

def meter_data(cur,total):
    global old
    if cur<=0:
        print(' '*(len(size(total))-1) + "? / " + size(total) + ' = ???% (Unknown remaining)\r')
    else:
        per = round(100*cur/total)

        if cur-old > 0 and per >= 5:
            rem = round(meter_buff * (total-cur) / (cur-old))
            m, s = divmod(rem, 60)
            h, m = divmod(m, 60)
            remain = (str(h) + ':') if (h > 0) else ''
            remain = remain + str(m).zfill(2) + ':' + str(s).zfill(2)
        else:
            remain = 'Unknown'

        print(size(cur) + " / " + size(total) + ' = ' + str(per).zfill(3) + '% (' + remain + ' remaining)\r')
        old = cur

def copy(source, destination): 
    global meter_buff
    global old
    meter = True
    meter_buff = 1.0 #secs
    sourcesh = shlex.quote(source)
    destinationsh = shlex.quote(destination)

    if not existf(source):
        print('Source not found')
        return False
    if existf(destination):
        inp='_'
        while inp[0] != 'c':
            inp = input('Destination exists. (C)ontinue or (A)bort? ').lower() + '_'
            if inp[0] == 'a': return False

    source_size = 0
    if not test_run: source_size = getsize(source)
    old = 0

    if not existf(destination): os.makedirs(destination)
    
    class CopyThread(threading.Thread):
        def run(self):
            subprocess.call(cmd,shell=True)
            
    def progress(dest):
        if existf(dest):
            meter_data(getsize(dest),source_size)

    cmd = copycmd + " " + sourcesh + " " + destinationsh
    if test_run:
        print('Terminal command:',cmd)
        return True
    
    tc = CopyThread(args=(cmd))
    tc.start()
    
    meter_data(0,source_size)

    ## find rsync's temp file    
    #while tempf=='None' and tc.isAlive(): tempf = findtempf(destination)
    #tempf = getnames(destination)[0] + tempf
    #
    #while existf(tempf) and meter:
    while tc.isAlive() and meter:
        tp = threading.Timer(meter_buff, progress, [destination])
        tp.start()
        tp.join()

    if meter: meter_data(getsize(destination),source_size)
    tc.join()
    return True
        
def checksum(file):
    sha1 = hashlib.sha1()
    bsize = 0x20000000
    f = None

    try:
        f = open(file, 'rb')
    except:
        return None

    fsize = getsize(file)

    header = "blob " + str(fsize) + "\0"
    sha1.update(header.encode('utf-8'))
    while True:
        buf = f.read(bsize)
        if not buf: break
        sha1.update(buf)
    f.close()

    return sha1.hexdigest()

def check(source, destination):
    if test_run or not existf(destination): return 'N/A'
    
    c1,c2=None,None
    if comprehensive:
        c1 = checksum(source)
        c2 = checksum(destination)
    else:
        c1 = getsize(source)
        c2 = getsize(destination)
    print('SOURCE      = '+str(c1)+'\nDESTINATION = '+str(c2))
    print('DIFFERENCE  = '+size(c2-c1))
    return (c1==c2) and (c1!=None)

def getcard(cam):
    start_roll = 1
    if manual: return input('Card Number: ')
    
    cards = []
    for root, dirs, files in os.walk(diskroot+drive01+'/'+folder(0)):
        cards = cards + [d[5:] for d in dirs if d[:5]=='CARD_']

    if multi_cam: cards = [c[1:] for c in cards if c[:1]==cam]

    temp = []
    for c in cards:
        if c.isdigit(): temp = temp + [int(c)]
        else: print(cam + c + ' omitted from card count.')
    cards = temp

    if len(cards)==0: return start_roll
    return max(cards)+1

def correctdate(dt):
    a_day = datetime.timedelta(days=1)
    
    if dt.hour < AM_CUT and not overnight: dt = dt - a_day
    elif overnight and dt.hour < PM_CUT: dt = dt - a_day
    if yesterday: dt = dt - a_day

    return dt

def getday(dt):
    dgts = 2
    start_day = 1
    if manual: return input('Day Number: ')
    
    days = []
    for root, dirs, files in os.walk(diskroot+drive01+'/'+folder(0)):
        days = days + [d for d in dirs if d[:3]=='DAY']
        
    if dt.date() == correctdate(datetime.datetime.now()).date():
        datetext = str(dt.year)[-2:]+'-'+str(dt.month).zfill(2)+'-'+str(dt.day).zfill(2)
        matches = [int(d[3:3+dgts]) for d in days if datetext in d and d[3:3+dgts].isdigit()]
        if len(matches)>0: return matches[0]

    days = [d[3:3+dgts] for d in days]

    temp = []
    for d in days:
        if d.isdigit(): temp = temp + [int(d)]
        else: print('DAY' + d + ' omitted from card count.')
    days = temp

    if len(days)==0: return start_day
    return max(days)+1


def folder(n):
    
    if n==0:
        return project
    
    if n==1:
        dt = correctdate(datetime.datetime.now())

        num = getday(dt)
        
        y,m,d = str(dt.year),str(dt.month),str(dt.day)
        if manual:
            y = input('Year: ')
            if len(y)>2: y = y[-2:]
            m = input('Month: ')
            d = input('Date: ')
        y,m,d = y[-2:],m.zfill(2),d.zfill(2)
            
        return 'DAY'+str(num).zfill(2)+'_'+y+'-'+m+'-'+d
    
    if n==2:
        cam = ''
        if multi_cam: cam = input('Cam letter: ')[:1].upper()
        cardnum = getcard(cam)
        return 'CARD_'+cam+str(cardnum).zfill(2)#=> 3 if 100+ cards expected
    return None

def drivetest(dest):
    while not os.path.isdir(dest):
        temp = input(dest[len(diskroot)-1:]+' not found. (R)etry or (S)kip? ').upper()
        if temp[:1]=='S':
            print('Drive skipped.')
            return False
    return True

def main():
    source = diskroot+media+'/'
    dest01 = diskroot+drive01
    dest02 = drive02
    if dest02!=None: dest02 = diskroot+dest02
    folders = '/'+folder(0)+'/'+folder(1)+'/'+folder(2)

    print()
    if drivetest(dest01):
        print('Copying "'+source+'" to "'+dest01+folders+'"')
        good = copy(source,dest01+folders)
        if not good: print('Error copying to '+drive01)
        if checkit: print('Size match: '+str(check(source,dest01+folders)))

    if drive02!=None:
        dest02 = diskroot+drive02
        print()
        if drivetest(dest02):
            print('Copying "'+source+'" to "'+dest02+folders+'"')
            good = copy(source,dest02+folders)
            if not good: print('Error copying to '+drive02)
            if checkit: print('Size match: '+str(check(source,dest02+folders)))
    else: print('\nDrive02 skipped.')

    # Additional output data ??
    print('\nRSync task completed.')

main()
