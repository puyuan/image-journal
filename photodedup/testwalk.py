import scandir
import os.path
import time
# Walk into directories in filesystem
# Ripped from os module and slightly modified
# for alphabetical sorting
#
from os.path import join, isdir, islink

def regularWalk(top):
    dict={}
    epoch=time.time()
    for root, dirs, files in scandir.walk(top):
        dict[root]=({}, {}, epoch)
        for dir in dirs:
            path=join(root, dir)
            dict[root][0][dir]=(path, epoch)
            #print path
        for file in files:
            path=join(root, file)
            dict[root][1][file]=(path, epoch)
            #print path
    return dict

def printDict(dict, root):

    print root.encode("utf-8")
    #print dict.get(root)
    dirs, files, epoch = dict.get(root, ({},{}, 0))
    print epoch
    for name, (path, timestamp ) in dirs.iteritems():
        print  path.encode("utf-8"), timestamp
    for name, (path, timestamp) in files.iteritems():
        print  path.encode("utf-8"), timestamp


    for name, (path, timestamp) in dirs.iteritems():
        printDict(dict, path)





def entry_compare(entry1, entry2):
    return entry1.name > entry2.name



def sortedWalk(top):


    dir_entries = scandir.scandir(top)
    entries=[entry for entry in dir_entries]
    entries.sort(entry_compare)

    for entry in entries:

        if entry.is_dir():
           for file in  sortedWalk(entry.path):
               yield file
        else:
            yield entry.path

dict=regularWalk("/cygdrive/f/Cleaned_Photos")
printDict(dict, "/cygdrive/f/Cleaned_Photos")