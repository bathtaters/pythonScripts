# Folder containing files to modify
inp_fold  = '/Metaless/'

# Folder containing files w/ data to be copied into files
#   Filenames should match files in inp_fold
copy_fold = '/OriginalMetadata/'

# Folder to output files to (Should be empty!)
out_fold  = '/Combined/'

# Chunks to copy from copy_fold [offset, size, insertOffset]
copyChunks = [
    (12, 6100, 12)
]

# Size chunks to update in input [offset, size, endian]
sizeChunks = [
    (4, 4, 'little')
]

# Data blocks to remove from input [offset, size]
removeChunks = [
    (12, 710),
    (770, 246)
]

# Ignore files
ignore = [ '.DS_Store' ]


buffer_size = 4096







import os


def getSizeDiff(addChunks, rmvChunks):
    diff = 0
    for achunk in addChunks:
        diff += achunk[1]
    for rchunk in rmvChunks:
        diff -= rchunk[1]
    return diff

def getCopyData(path, chunks):
    data = []
    with open(path, 'rb', buffer_size) as file:
        for chunk in chunks:
            file.seek(chunk[0], os.SEEK_SET)
            data.append((chunk[2], file.read(chunk[1])))
    return data

def getSizes(file, diff, chunks):
    data = []
    for chunk in chunks:
        file.seek(chunk[0], os.SEEK_SET)
        size = int.from_bytes(file.read(chunk[1]), chunk[2])
        data.append((chunk[0], (size + diff).to_bytes(chunk[1], chunk[2])))
    return data


def orderOperations(insertData, removeData, replaceData):
    # insertData  = [(offset, <bytes>)]
    # removeData  = [(offset, size   )]
    # replaceData = [(offset, <bytes>)]

    def sortOps(op):
        return op[0]
    
    ops = []
    for iOp in insertData:
        ops.append((iOp[0],'add',iOp[1]))
    for rOp in removeData:
        ops.append((rOp[0],'rmv',rOp[1]))
    for oOp in replaceData:
        ops.append((oOp[0],'rmv',len(oOp[1])))
        ops.append((oOp[0],'add',oOp[1]))
    ops.sort(key=sortOps)
    return ops


def writeOutFile(outPath, inFile, operations):
    inFile.seek(0, os.SEEK_END)
    inSize = inFile.tell()
    inFile.seek(0, os.SEEK_SET)
    
    with open(outPath, 'wb', buffer_size) as outFile:
        
        for op in operations:
            
            while (op[0] - inFile.tell() > buffer_size):
                outFile.write(inFile.read(buffer_size))
            
            if (op[0] > inFile.tell()):
                outFile.write(inFile.read(op[0] - inFile.tell()))
            
            if (op[1] == 'add'):
                outFile.write(op[2])
            elif (op[1] == 'rmv'):
                inFile.seek(op[0] + op[2], os.SEEK_SET)

        while (inSize > inFile.tell()):
            if (inSize - inFile.tell() < buffer_size):
                outFile.write(inFile.read(inSize - inFile.tell()))
                return
            outFile.write(inFile.read(buffer_size))
                


def main():
    os.makedirs(out_fold, exist_ok=True)

    size_diff = getSizeDiff(copyChunks, removeChunks)

    cnt = 0
    tot = 0

    print('Saving files...')
    for filename in os.listdir(inp_fold):
        
        if filename in ignore: continue
        tot += 1
        
        inp_path  = os.path.join(inp_fold, filename)
        copy_path = os.path.join(copy_fold,filename)
        out_path  = os.path.join(out_fold, filename)

        if (not(os.path.exists(copy_path))):
            print('File missing from Copy_Fold:',filename)
            continue

        copyData = getCopyData(copy_path, copyChunks)
        
        with open(inp_path, 'rb', buffer_size) as file:
            sizeData = getSizes(file, size_diff, sizeChunks)
            ops = orderOperations(copyData, removeChunks, sizeData)
            writeOutFile(out_path, file, ops)

        cnt += 1

    print('Wrote',cnt,'files of',tot)

main()
