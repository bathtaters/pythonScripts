# Match & rename Google Photo JSONs
# Download Google photos, then fill out below

# Path to Google Photos download (Will be searched recursively)
folder = "/path/to/google/photos/"

# "Deleted" files will be moved here
recycle = "/path/to/recycling/"

# True will print out renames (Without executing them)
TEST_MODE = True








# --- ADVANCED --- #

import os, re

JSON_EXT = 'json'

# REG-EXES
# Multi-filenames
mult_re = re.compile(r'(.+)((?=\(\d+\))\(\d+\))(\.\S+)?$')
# Files to remove
remove_re = re.compile(r'(.+)-edited([\.\(].+)$')
# JSON files
json_re = re.compile(r'(.+)\.'+JSON_EXT+'$')
# Multi-JSONs
jmult_re = re.compile(r'(.+)\((\d+)\)\.'+JSON_EXT+'$')



# --- SCRIPT --- #

def multizeName(name):

    mname = mult_re.search(name)
    if mname:
        result =  mname.group(1)
        if mname.group(3): result += mname.group(3)
        return multizeName(result)
    #print(" MULTIZE: -NO- :",name)
    return name

def matchFiles(root, json, image):
    c,n = '',0
        
    image = os.path.splitext(image)
    while os.path.exists(os.path.join(root,image[0] + c + image[1] + '.' + JSON_EXT)):
        n += 1
        c = '('+str(n)+')'

    if TEST_MODE: print("  RENAME:",json, image[0] + c + image[1] + '.' + JSON_EXT)
    else: os.rename(os.path.join(root,json), os.path.join(root,image[0]+ c +image[1]+'.'+JSON_EXT))

def deleteFile(root, image):
    moveto = root.replace(folder,recycle)
    if TEST_MODE: print("  MOVE:",image,'->',moveto[39:])
    else:
        os.makedirs(moveto, exist_ok=True)
        os.rename(os.path.join(root,image),os.path.join(moveto,image))



def main():
    multis = {}
    for root, dirs, files in os.walk(folder):
        print("\n"+root)
        jsons, unmatched = [], []
        removed, toremove = [], []
        
        for orig_name in files:
            sp_ind = orig_name.find('.')
            name = orig_name[:sp_ind] + orig_name[sp_ind:].lower()
            
            rname = remove_re.search(name)
            if rname:
                deleteFile(root, name)
                clean_name = rname.group(1) + rname.group(2)
                if clean_name in toremove: toremove.remove(clean_name)
                else: removed.append(clean_name)
                continue
            
            jname = json_re.search(name)
            if jname:
                jname = jname.group(1)
                
                mult = jmult_re.search(name)
                if mult:
                    multis.update([(os.path.join(root, mult.group(1)), mult.group(2))])
                
                if jname in unmatched: unmatched.remove(jname)
                else: jsons.append(name)
                
            else:
                if name in removed: removed.remove(name)
                else: toremove.append(name)
                if name in jsons: jsons.remove(name)
                else: unmatched.append(name)

        remaining = []
        unmatched_noext = [ multizeName(os.path.splitext(name)[0]) for name in unmatched ]
        for name in jsons:
            jname = multizeName(json_re.search(name).group(1))
            cut = os.path.splitext(jname)[0]
            if cut in unmatched_noext:
                index = unmatched_noext.index(cut)
                matchFiles(root, name, unmatched[index])
                unmatched.pop(index)
                unmatched_noext.pop(index)
                continue
            
            for match in unmatched_noext:
                if cut == match[:len(cut)]:
                    index = unmatched_noext.index(match)
                    matchFiles(root, name, unmatched[index])
                    unmatched.pop(index)
                    unmatched_noext.pop(index)
                    break
                
            else: remaining.append(name)

        if len(remaining) > 0:
            yn = input("  "+str(len(remaining))+" unmatched file(s). Print (y/n)? ")
            if yn.strip()[0].lower() == 'y':
                print("  UNMATCHED JSONS:\n\t",'\n\t'.join(remaining),sep='')
        if len(removed) > 0:
            yn = input("  "+str(len(removed))+" missing original(s). Print (y/n)? ")
            if yn.strip()[0].lower() == 'y':
                print("  MISSING ORIGINAL IMAGE:\n\t",'\n\t'.join(removed),sep='')

    if len(multis) > 0:
        yn = input("\n"+str(len(multis))+" multi-file(s). Print (y/n)? ")
        if yn.strip()[0].lower() == 'y':
            print("\nMULTI-FILES:")
            for key,val in multis.items():
                print('  ',key.replace(folder,''),'=',val)


main()
