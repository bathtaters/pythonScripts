# Create countdown caption file for AVID


# Filepath to save
# WARNING: Will not ask before overwriting
OUT_FILE = '/Users/Nick/Desktop/AVIDTEST.txt'#'/path/to/output.txt'

# Countdown range
COUNTDOWN_START = [0,10] # [Mins,Secs] or [Secs]
COUNTDOWN_END = [0,1] # [Mins,Secs] or [Secs]

# Timecode to start countdown
TC_START = [0,0,50,0] # [Hrs,Mins,Secs,Frames]
FRAMERATE = 24 # Frames per second





# Increment options
COUNTDOWN_INC = -1 # seconds
TC_INC = -1 * COUNTDOWN_INC * FRAMERATE # frames






LIMIT_DICT = { 1 : [100],
               2 : [100,60],
               4 : [100,60,60,FRAMERATE] }

def array_to_int(time_array):
    limit = LIMIT_DICT[len(time_array)]
    count = 0
    for i in range(len(time_array)):
        count = count * limit[i] + time_array[i]
    return count

def disp_time(time_array):
    disp = ''
    for t in time_array:
        disp = disp + str(t).zfill(2) + ':'
    return disp[:-1]

def add_time(time_array,value):
    limit = LIMIT_DICT[len(time_array)]

    carry = value
    for p in range(len(time_array)-1,-1,-1):
        time_array[p] = time_array[p] + carry
        carry = 0
        while time_array[p] >= limit[p]:
            time_array[p] = time_array[p] - limit[p]
            carry = carry + 1
        while time_array[p] < 0:
            time_array[p] = time_array[p] + limit[p]
            carry = carry - 1

    if carry > 0: print('ERROR')

    return time_array

def main():
    total_secs = array_to_int(COUNTDOWN_END) - array_to_int(COUNTDOWN_START)
    print('Creating file with', total_secs // COUNTDOWN_INC, 'entries.')
    with open(OUT_FILE,'w') as f:       
        f.write('@ This file created by captionGen_Avid.py\n\n<begin subtitles>\n')

        tc,counter = TC_START,COUNTDOWN_START
        while array_to_int(counter) * COUNTDOWN_INC <= array_to_int(COUNTDOWN_END) * COUNTDOWN_INC:
            f.write(disp_time(tc)+' ')
            add_time(tc,TC_INC)
            f.write(disp_time(tc)+'\n'+disp_time(counter)+'\n\n')
            if COUNTDOWN_END == counter: break
            add_time(counter,COUNTDOWN_INC)

        f.write('<end subtitles>\n')
        f.flush()
    print('Complete')
        
    
main()
