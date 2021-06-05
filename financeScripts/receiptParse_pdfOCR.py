# PDF/IMG to PDF/A w/ OCR
#
# Converts images/pdfs to text-embedded PDF/As in all subdirectories
# Use main() for input prompts
# Use default() to use below settings
# Or use main(folder_path,VERBOSE,OVERWRITE,SKIP_OCR,TXT_MODE)
# To force-convert a single pdf using default settings use convert_to_pdfA(infile, outfile)


# DEPENDENCIES:
import os, tempfile, subprocess, shutil, sys
# SHELL SCRIPTS REQUIRED:
#   tesseract: OCR engine
#   pdftk: combines output pgs to pdf
#   pdftoppm: opens/splits pdf to pgs (Included w/ poppler/xpdf)
#   pdftotext: reads text-layer of pdf (Included w/ poppler/xpdf) 
pdftk = '/usr/local/bin/pdftk'
tesseract = '/usr/local/bin/tesseract'
pdftoppm = '/usr/local/bin/pdftoppm'
pdftotext = '/usr/local/bin/pdftotext'




# SETTINGS for default()
# Don't need to set these if you're using receiptParse_main.py

# Path of files to convert (Will walk all sub directories recursively)
folder_path = '/path/to/PDFs/'

# Verbose output
VERBOSE = False

# Overwrite PDFs (False will create subdirectory with OCR PDFs)
OVERWRITE = True

# Skip PDFs that already contain text
SKIP_OCR = False

# Output new text file with data (False outputs PDF w/ text layer)
TXT_MODE = False


























# Advanced options
BYPASS_DEPENDS = False
SKIP_FILES = ('.DS_Store',)

# File/Folder suffix to use (Must NOT be '')
SUFF = 'ocr'












##### SCRIPT START ######


# Test if dependancies are installed:
DEPENDS = (pdftk, tesseract, pdftoppm, pdftotext) # list of dependency names
for d in DEPENDS:
    if not os.path.exists(d):
        d_str = None
        for k, v in list(globals().items()):
            if v is d and k != 'd':
                d_str = k
        print('ERROR: Dendancy path invalid (Or missing):',d_str,d)
        if not BYPASS_DEPENDS: sys.exit()

            
def has_text(filepath):
    # Get any PDF-text
    text = shell([pdftotext, filepath, '-'])
    # Strip out all whitespace and blanklines
    text = ''.join([line.strip() for line in text.splitlines()]).strip()
    return text!=''

# Ignore lines that start with these when error-checking shell output
ERR_SKIP = ('Tesseract Open Source OCR Engine','Warning','Estimating resolution')
def shell(cmd):
    # RUN SHELL CMD
    x = subprocess.run(cmd, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if x.stdout != b'':
        ret = []
        for line in x.stdout.decode().splitlines():
            for estr in ERR_SKIP:
                if estr.lower() == line[:len(estr)].lower(): break
            else:
                ret.append(line)
        ret = '\n'.join(ret)
        if ret != '':
            if ret[-1]=='\n': ret = ret[:-1]
            return '\t\t' + ret.replace('\n','\n\t\t')
    return 0

def combine_pages(indir,outfile,ext='pdf'):
    ext = ext.lower().replace('.','')
    pdfs = [ os.path.join(indir,p) for p in os.listdir(indir) \
             if os.path.splitext(p)[1].lower().replace('.','') == ext ]
    if not pdfs: return -1
    
    x = shell([pdftk,*pdfs,'output',outfile])
    if type(x) is str:
        # Combiner returned error
        if VERBOSE: print('\t',end='')
        log.append('Error repacking\n'+x)
        print('Error repacking',p)
        if VERBOSE: print(x)
        shutil.rmtree(new_dir)
        return 1
    return 0
        
PG_EXT = os.extsep+'ppm'
def convert_to_pdfA(infile,outfile,log=[]):
    # MAIN CONVERTER, USES SHELL()
    new_dir = tempfile.mkdtemp() + os.sep
    pg, eg = 0, 0
    ppath,p = os.path.split(infile)
    ppath += os.sep

    # Open PDF split into images
    x = shell([pdftoppm,ppath+p,new_dir+'p'])
            
    if type(x) is str:
        # PDFtoPPM returned error
        if VERBOSE: print('\t',end='')
        log.append('Error unpacking\n'+x)
        print('Error unpacking',p)
        if VERBOSE: print(x)
        shutil.rmtree(new_dir)
        return (1,pg,eg)

    # Convert PPMs to OCR PDFs
    for f in os.listdir(new_dir):
        if PG_EXT not in f:
            # Not a PPM
            os.remove(new_dir+f)
            continue
        
        # Run google OCR on JPG
        opt = 'pdf'
        if TXT_MODE: opt = ''
        x = shell([tesseract,new_dir+f,new_dir+f.replace(PG_EXT,SUFF)]+opt.split())
        pg += 1
        if type(x) is str:
            # Tesseract returned error
            eg += 1
            log.append('Tesseract output (Page:'+f+'):\n'+x)
            if VERBOSE:
                print('\t',end='')
                print(log[-1])
        os.remove(new_dir+f)
    
    # List converted files
    pdfs = [ new_dir+f for f in os.listdir(new_dir) if os.extsep+('pdf','txt')[TXT_MODE] in f ]
    pdfs.sort()

    if TXT_MODE:
        # Combine in text file
        with open(outfile,'wb') as outf:
            for t in pdfs:
                size = os.path.getsize(t)
                with open(t,'rb') as inf:
                    outf.write(inf.read(size))
                outf.write(b'\n')
                outf.flush()
                os.remove(t)

    else:
        # Combine into PDF
        x = shell([pdftk,*pdfs,'output',outfile])
        if type(x) is str:
            # Combiner returned error
            e += 1
            if VERBOSE: print('\t',end='')
            log.append('Error repacking\n'+x)
            print('Error repacking',p)
            if VERBOSE: print(x)
            shutil.rmtree(new_dir)
            return (1,pg,eg)
        
    shutil.rmtree(new_dir)
    return (0,pg,eg)




def convert_dir(top_dir):
    print('Converting all PDF files under',top_dir)
    if VERBOSE: print()

    # Init vars
    c,t,s,pg,e,eg = 0,0,0,0,0,0
    suffix,ext = SUFF + os.sep,'pdf'
    if OVERWRITE: suffix = ''
    if TXT_MODE: ext = 'txt'
    
    # Path Walk Loop
    for pdf_path, subs, files in os.walk(top_dir):
        # Remove skipped files then skip empty directories
        pdfs = [ f for f in files if f not in SKIP_FILES ]
        if len(pdfs) < 1: continue 
        
        # Make directory for writing new PDFs to
        if pdf_path[-1] != os.sep: pdf_path += os.sep
        pdf_out = pdf_path + suffix
        if not os.path.exists(pdf_out): os.makedirs(pdf_out)
        
        # Directory loop
        if VERBOSE: print('Converting PDF files in',pdf_path.replace(top_dir,os.curdir+os.sep)[:-1])
        dc,dt,ds,dpg,de,deg = 0,0,0,0,0,0
        for p in pdfs:
            if os.extsep+'pdf' not in p:
                # File is not PDF
                ds += 1
                continue
            elif SKIP_OCR and has_text(pdf_path+p):
                # Is already PDF-A
                print(p,'already contains text')
                dt += 1
                continue

            if VERBOSE: print('Converting',p)
            # Increment vars and run converter method
            dc += 1
            r = convert_to_pdfA(pdf_path+p,pdf_out+p.replace(os.extsep+'pdf',suffix[:-1]+os.extsep+ext))
            de,dpg,deg = de + r[0], dpg + r[1], deg + r[2]

        # Remove empty OCR folders
        if dc < 1:
            if pdf_out != pdf_path: os.rmdir(pdf_out)
            if VERBOSE: print('No valid files found.\n')
        # Increment master counters 
        elif VERBOSE:
            print('Successfully converted',dc-de,'of',dc,'files and',dpg-deg,'of',dpg,'pages.')
            print('Skipped',ds+dt,'files.',end=' ')
            if ds+dt > 0: print(dt,'already contained text and',ds,'were not PDFs.\n')
            else: print('\n')
        c,t,s,pg,e,eg = c+dc,t+dt,s+ds,pg+dpg,e+de,eg+deg
        
    # Results
    if VERBOSE: print('OVERALL:')
    print('Successfully converted',c-e,'of',c,'files and',pg-eg,'of',pg,'pages.')
    print('Skipped',s+t,'files.',end=' ')
    if s+t > 0: print(t,'already contained text and',s,'were not PDFs.')
    else: print()

    return e


# USE MAIN METHOD
def main(top_dir='',v=VERBOSE,w=None,s=None,t=False):
    global OVERWRITE, SKIP_OCR, VERBOSE, TXT_MODE

    OVERWRITE, SKIP_OCR = w,s
    
    # Get top directory to begin sub-directory search
    while not os.path.exists(top_dir):
        if top_dir != '': print('Path is invalid.', end=' ')        
        top_dir = input('Enter path containing PDFs: ').strip()
    if top_dir[-1] != os.sep: top_dir += os.sep
    if v: print('Using path:',top_dir,end='\n\n')

    # Select overwrite/create new file mode
    if OVERWRITE == None:
        if v: print('Answering "no" will create "'+SUFF+'" folder within each subdirectory.')
        ui = input('Write over PDFs (y/n)? ')
        if ui.strip().lower()[0] != 'y': OVERWRITE = False
        else: OVERWRITE = True
    if v: print('Overwrite mode',('disabled.','enabled.')[OVERWRITE],end='\n\n')

    # Choose to skip already-ocr'd files
    if SKIP_OCR == None:
        if OVERWRITE and v: print('Answering "yes" will remove any text already inside PDFs.')
        ui = input('Skip PDFs already containing text (y/n)? ')
        if ui.strip().lower()[0] != 'n':SKIP_OCR = True
        else: SKIP_OCR = False
    if v: print('Skip PDF/A mode',('disabled.','enabled.')[OVERWRITE],end='\n\n')

    TXT_MODE = t
    if v: print('Output to',('pdf.','txt.')[TXT_MODE])
    
    # State if verbose mode is enabled
    VERBOSE = v
    if v: print('Verbose mode enabled.\n')
    
    
    return convert_dir(top_dir)

def default(top_dir=folder_path):
    # USE DEFAULT OPTIONS
    return main(top_dir,VERBOSE,OVERWRITE,SKIP_OCR,TXT_MODE)

def receiptOCR(pdf_file,txt_file, v=False, log=[]):
    global OVERWRITE, SKIP_OCR, VERBOSE, TXT_MODE
    OVERWRITE = False
    SKIP_OCR = False
    VERBOSE = v
    TXT_MODE = True

    if VERBOSE: print('Converting',pdf_file[pdf_file.rfind('/')+1:],
                      'to',txt_file[txt_file.rfind('/')+1:]+'...')
    ret = convert_to_pdfA(pdf_file,txt_file, log)
    if VERBOSE:
        if ret[0]: print('Conversion failed.')
        else: print('Succesfully converted, with',ret[2],'errors on',ret[1],'pages.')
    return -ret[0]

#default(folder_path)
