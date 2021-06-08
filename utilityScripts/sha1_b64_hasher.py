# BASE-64 FILE HASHER (Uses SHA1, returns Base64 string)
# Sets hasher (global var) to hash obj for additional manipulation

import hashlib,base64

BLOCKSIZE = 65536
hasher = None

def digest(file_path):
    global hasher
    hasher = hashlib.sha1()
    with open(file_path,'rb') as f:
        size = f.seek(0,2)
        print('HASHING FILE ['+str(size)+' bytes]...')
        f.seek(0,0)
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)

    return base64.b64encode(hasher.digest()).decode()


print('Use digest(file_path): returns base64 SHA1 string (Sets "hasher" to hash object)')
