# Download CSVs from SoundDevices recorder
# NOTE: Expects SoundDevices media is mounted on Mac OSX

day_start,day_end = 1,100
project = 'PROJ_NAME'
volume = '788T HDD'
report_title = 'SOUND_REPORT.CSV'
new_title = '%f_SoundReport.csv' # %f = inner folder title

save_dir = '/path/to/folder/'

overwrite = False






import os, shutil

def newroll(roll,n):
    # Converts %f '14Y01M01' to DAY01_01-01-2014
    convert_date = True
    include_day_num = True
    century_prefix = '20'
    seperator = '-'
    daynum_prefix = 'DAY'
    daynum_seperator = '_'
    daynum_len = 2 # 2 = '01'; 3 = '001'

    if not(convert_date) or len(roll)!=8: return roll
    y = roll[0:2]
    m = roll[3:5]
    d = roll[6:8]
    if (y+m+d).isnumeric() and roll[2]=='Y' and roll[5]=='M':
        roll = m + seperator + d + seperator + century_prefix + y
        if include_day_num:
            roll = daynum_prefix + str(n+1).zfill(2) + daynum_seperator + roll
    return roll

if not(os.path.isdir(save_dir)): os.mkdir(save_dir)
folder = '/Volumes/'+volume+'/'+project+'/'
days = os.listdir(folder)
for i in range(len(days),0,-1):
    if '.' == days[i-1][:1]: days.pop(i-1)
files = sorted(days)

s = max(day_start,1)
e = min(day_end,len(days))

for d in range(s-1,e):
    print('Outputing sound report '+str(i))
    source = folder + days[d] + '/' + report_title
    roll = newroll(days[d],d)
    dest = save_dir + new_title.replace('%f',roll)
    if not(os.path.exists(dest)) or overwrite:
        try:
            shutil.copy2(source, dest)
        except:
            print('Error.')
    else: print('File exists, not copied.')
    i = i + 1

print('Completed.')
