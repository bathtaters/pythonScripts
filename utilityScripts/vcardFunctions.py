DESC="""
                        VCARD FUNCTIONS   
                        ---------------
The following functions can be used to manipulate/parse VCards.

 - dupeNumbers(vcard_file_in, verbose = True)
     Returns an array of all duplicate phone numbers in vcard_file_in.
     verbose = True will notify whenever a match is found.


 - splitNames(vcard_file, new_vcard_file):
     Take all full names combined in the First Name field and split them up.
     Splits into first/last/etc name on spaces and saves to new_vcard_file.
     EX.: fn:"Bob Dole" ln:"" >> BECOMES >> fn:"Bob" ln:"Dole"


 - removeEmails(vcard_file, new_vcard_file)
     Removes all emails from vcard_file.
     Saves to new_vcard_file.


 - combineDupeEmails(vcard_file_in, vcard_file_out, ignore_term = None)
     Runs findEmails on vcard_file_in, then runs askNames on result,
     then runs makeNewVCard on the result of that saving to vcard_file_out.
     NOTE: Uses TEMP_EMAIL_LIST as a temporary file, deletes upon success
     
     - findEmails(vcard_file, email_list_file, filter_term = None)
         Create a list of all emails in vcard_file.
         If present, ignore emails containing filter_term.
         Saves to email_list_file.
         
     - askNames(email_list_in, email_list_out = None)
         Asks user for name related to each email from email_list_in.
         Saves to email_list_out, or overwrites if not given.
         
     - makeNewVCard(vcard_file, new_vcard_file, email_list_file)
         Creates new_vcard_file, based on vcard_file,
         using instructions from email_list_file.
         email_list_file should be email_list_out from askNames()
         

  - vcardHelp(): Print this help


"""


# FILE WILL BE CREATED/DELETED BY combineDupes
TEMP_EMAIL_LIST = '/tmp/com.python.vcard.emailList'








## --- METHODS --- ##

import os

def vcardHelp(): return print(DESC,'\nCONSTANTS: TEMP_EMAIL_LIST = "'+TEMP_EMAIL_LIST+'"\n')


def dupeNumbers(vcard_file_in, verbose = True):
    vcards = open(vcard_file_in,mode='r').readlines()
    nums = []
    numc = []

    if verbose: print('List of duplicate numbers:')
    for line in vcards:
        if line[:4]=='TEL;':
            for i,n in enumerate(nums):
                if n == line[9:-1]:
                    numc[i] = numc[i] + 1
                    if verbose: print('"'+line+'" has '+numc[i]+' matches.')
                    break
            else:
                nums.append(line[9:-1])
                numc.append(0)

    vcards.close()

    dupes = [ nums[i] for i in range(len(nums)) if numc[i] ]
    print('Found',len(dupes),'matches.') 
    return dupes
    



def splitNames(vcard_file_in, vcard_file_out):
    vcards = open(vcard_file_in,mode='r').readlines()
    output = ''

    for line in vcards:
        if line[:2]=='N:':        
            name = ['']*4
            n = 0
            for c in line[2:-1]:
                if c!=';': name[n] = name[n] + c
                else: n=n+1
            
            if name[1]=='' and ' ' in name[0]:
                name = name[0].split()
                name.insert(0,name[len(name)-1])
                name.pop()
                while len(name)<4: name.append('')

            newline = 'N:'
            for i in range(4):
                newline = newline + name[i] + ';'
            
            if newline!=line[:-1]: print(newline)
            output = output + newline + '\n'
        
        else: output = output + line
        
    vcards.close()

    input('\nWill overwrite "'+vcard_file_out+'"')
    newfile = open(vcard_file_out,mode='w',buffering=-1,encoding='utf8')
    newfile.write(output)
    newfile.close()



def removeEmails(vcard_file, new_vcard_file):
    vcards = open(vcard_file,mode='r').readlines()
    output,buffer = '',''
    save = True

    for line in vcards:

        if line[:6]=='BEGIN:':
            if save: output = output + buffer
            save = True
            buffer = ''
        elif line[:2]=='N:':
            if ('@' in line) or line[:-1]=='N:;;;;': save = False
        buffer = buffer + line

    vcards.close()

    
    input('Will overwrite "'+new_vcard_file+'"')
    newfile = open(new_vcard_file,mode='w',buffering=-1,encoding='utf8')
    newfile.write(output)
    newfile.close()



def findEmails(vcard_file, email_list_file, filter_term = None):
    vcards = open(vcard_file,mode='r').readlines()
    output = ''
    lookup = False

    for line in vcards:

        if line[:6]=='BEGIN:': lookup = False
        elif line[:2]=='N:':
            if ('@' in line) or line[:-1]=='N:;;;;': lookup = True
        elif line[:5]=='EMAIL' and lookup:
            email = ''
            for i in range(2,len(line)):
                if line[-i]==':': break
                email = line[-i] + email
            if not filter_term or not(filter_term in email): output = output + email + '\n'
            
    vcards.close()

    
    print(output)
    input('\nWill overwrite "'+email_list_file+'"')
    newfile = open(email_list_file,mode='w',buffering=-1,encoding='utf8')
    newfile.write(output)
    newfile.close()
    


def makeNewVCard(vcard_file,new_vcard_file,email_list_file):

    def readEmailList(email_list_file):
        txt = open(email_list_file, mode='r').readlines()
        out = []
        for line in txt:
            lines = line.split(',')
            name = lines[1].split()
            name.insert(0,name[len(name)-1])
            name.pop()
            while len(name)<4: name.append('')
            lines[1] = ''
            for i in range(4): lines[1] = lines[1] + name[i] + ';'
            out = out + [lines]
        txt.close()
        return out
    
    emails = readEmailList(email_list_file)

    vcards = open(vcard_file,mode='r').readlines()
    output,buff,new = '','',''
    to_buff,lookup,cont = True,False,False

    for line in vcards:

        if line[:6]=='BEGIN:': to_buff,lookup,cont,output,new,buff = True,False,False,output+new,'',''
        elif (line[:2]=='N:' and '@' in line) or line[:-1]=='N:;;;;': lookup = True
        elif line[:5]=='EMAIL' and lookup and to_buff:
            email = ''
            for i in range(2,len(line)):
                if line[-i]==':': break
                email = line[-i] + email
            for entry in emails:
                if entry[0]==email:
                    if entry[1]=='DELETE;;;;':
                        buff,to_buff,cont = '',True,False
                        break
                    new = 'BEGIN:VCARD\nVERSION:3.0\nN:'+entry[1]+'\n'+buff+line
                    buff = ''
                    to_buff,cont = False,True
                    break
            if not(cont): to_buff,buff = False,''
        elif lookup:
            if to_buff: buff = buff + line
            if cont: new = new + line

    vcards.close()
    

    input('Will overwrite "'+new_vcard_file+'"')
    newfile = open(new_vcard_file,mode='w',buffering=-1,encoding='utf8')
    newfile.write(output)
    newfile.close()



def askNames(email_list_in, email_list_out = None):
    if not email_list_out: email_list_out = email_list_in
    
    emails = open(email_list_in).readlines()
    output = ''
    prev = ''

    print('Enter name cooresponding to email. If email is a duplicate write "same."')
    for line in emails:
        line = line[:-1]
        name = input(line + ': ')
        if name.upper()=='SAME': name = prev
        prev = name
        output = output + line + ',' + name + '\n'
    emails.close()
        
    print(output)
    input('Will overwrite "'+email_list_out+'"')
    newfile = open(email_list_out,mode='w',buffering=-1,encoding='utf8')
    newfile.write(output)
    newfile.close()



def combineDupeEmails(vcard_file_in, vcard_file_out, ignore_term = None):
    findEmails(vcard_file_in, TEMP_EMAIL_LIST, ignore_term)
    askNames(TEMP_EMAIL_LIST)
    makeNewVCard(vcard_file_in, vcard_file_out, TEMP_EMAIL_LIST)
    os.remove(TEMP_EMAIL_LIST)


print('VCard functions loaded. Enter vcardHelp() for details.')

