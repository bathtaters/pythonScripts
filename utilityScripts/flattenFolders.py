# Flatten a nested folder structure
# Takes all children of all subfolders and moves them to destination folder
# NOTE: Only goes 1 layer deep

# Parent folder to flatten
dr = '/path/to/parent/folder'
# New folder to move nested files into
dest = 'destination_folder'


## SCRIPT

import os

folds = os.listdir(dr)
os.mkdir(dr+'/'+dest)
for fold in folds:
    if dest not in fold: continue
    print(fold)
    fils = os.listdir(dr+'/'+fold)
    for fil in fils:
        if fil=='.DS_Store': continue
        save_as = dr+'/'+dest+'/'+fil
        y,saved = 0,save_as
        while os.path.exists(saved):
            x = save_as.rfind('.')
            saved = save_as[:x] + '_' + str(y) + save_as[x:]
            y = y + 1
            
        os.rename(dr+'/'+fold+'/'+fil,saved)
            
print('DONE')
