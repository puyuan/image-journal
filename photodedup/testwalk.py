import os.path
import time
import sys
import pickle
# Use the built-in version of scandir/walk if possible, otherwise
# use the scandir module version
try:
        from os import walk
except ImportError:
        from scandir import scandir, walk

# Walk into directories in filesystem
# Ripped from os module and slightly modified
# for alphabetical sorting
#
from os.path import join, isdir, islink

def regularWalk(top, dict={}):
    epoch=time.time()
    dict['last_accessed_time']=epoch
    root_entries=dict.setdefault('roots', {})
    countfiles=0
    countdirs=0

    for root, dirs, files in walk(top):
        root_entry=root_entries.setdefault(root,[{}, {}, epoch, epoch])
        root_entry[3]=epoch
        
        for dir in dirs:
            path=join(root, dir)
            dir_entry=root_entry[0].setdefault(dir, [path, epoch, epoch])
            dir_entry[2]=epoch
        for file in files:
            path=join(root, file)
            file_entry=root_entry[1].setdefault(file, [path, epoch, epoch])
            file_entry[2]=epoch

        countfiles+=len(files)
        countdirs+=len(dirs)
        sys.stdout.write("Processing %d dirs, %d files \r" %(countdirs, countfiles))
        sys.stdout.flush()
    return dict

def printDict(dict, root):

    last_accessed_time=dict.get('last_accessed_time', '')
    root_entries=dict.get('roots', {})

    #print dict.get(root)
    dirs, files, create_time, modified_time = root_entries.get(root, [{},{}, 0, 0])
    for name, (path, create_time, modified_time)  in dirs.iteritems():
        if modified_time != last_accessed_time:
            print  (path, modified_time)
    for name, (path, create_time, modified_time)  in files.iteritems():
        if modified_time < last_accessed_time:
            print path
        elif create_time == last_accessed_time:
            print path


    for name, (path, create_time, modified_time) in dirs.iteritems():
        printDict(dict, path)

def checkPruning(dict):
    last_accessed_time=dict.get('last_accessed_time', '')
    root_entries=dict.get('roots')
    print (last_accessed_time)

    for root, (dirs, files, create_time, modified_time) in root_entries.iteritems():
        if not files:
            continue

        for name, (path, create_time, modified_time)  in dirs.iteritems():
            if modified_time != last_accessed_time:
                print  (path.encode("utf-8"), modified_time)
        for name, (path, create_time, modified_time)  in files.iteritems():
            print create_time
            if modified_time < last_accessed_time:
                print path
            elif create_time == last_accessed_time:
                print path



def saveDict(dict):
    output = open('dict.pkl', 'wb')
    # Pickle dictionary using protocol 0.
    pickle.dump(dict, output)
    output.close()

def loadDict():
    try:
        file = open('dict.pkl', 'rb')
        # Pickle dictionary using protocol 0.
        output=pickle.load(file)
        file.close()
    except:
        return {}
    return output



path="/cygdrive/c/Windows/Temp"
dict=regularWalk(path, loadDict())
printDict(dict, path)
#checkPruning(dict)
saveDict(dict)
