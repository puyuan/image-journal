#!/usr/bin/env python
import Queue
import threading
import urllib2
import time
import sqlite3
import os
import json
import hashlib
from dateutil.parser import parse
from dateutil.relativedelta import *
from math import ceil
import re

hosts = ["http://yahoo.com", "http://google.com", "http://amazon.com",
        "http://ibm.com", "http://apple.com"]

queue = Queue.Queue()

def processImage(row):
    sourceFile=row[4]
    correctedDate=re.sub(r'(\d{4}):(\d{2}):(\d{2}\s+\d{2}:\d{2}:\d{2}).*',r'\1-\2-\3', row[0])
    try:
        parsedDate=parse(correctedDate)
    except:
        return
    #md5sum=hashlib.md5("%s:%s:%s:%s:%s"%(parsedDate.year,parsedDate.month, parsedDate.day,parsedDate.hour,parsedDate.minute)).hexdigest()
    parsedDate=parsedDate.replace(second=0, microsecond=0)
    print(parsedDate.isoformat())
    md5sum=parsedDate.isoformat().replace(":", "")

    dic=dict(row)
    dic["thumb"]="images/%s_t.jpg"%md5sum
    dic["src"]="images_wide/%s.jpg"%md5sum
    dic["group"]="%d-%d"%(parsedDate.year,parsedDate.month)
    dic["date"]=parsedDate.date().isoformat()
    #dic["group"]="%d-%d-%d"%(parsedDate.year,parsedDate.month,week_of_month(parsedDate))
    sourceFile=dic["SourceFile"].encode("utf-8")
    imageDir="images_original/%s/%s"%(parsedDate.year, parsedDate.month)
    print(sourceFile, md5sum)
    if (not os.path.isfile("images/%s_t.jpg"%md5sum)):
        os.system("convert  -auto-orient -thumbnail x300 \"%s\"  images/%s_t.jpg" %(sourceFile, md5sum ))
    if (not os.path.isfile("%s/%s.jpg"%(imageDir, md5sum))):
        os.system("convert \"%s\" -channel rgb -auto-level  -resize 1920x1080^  -auto-orient -quality 86   %s/%s.jpg" %(sourceFile,imageDir,  md5sum ))

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, threadName):
        threading.Thread.__init__(self)
        self.queue = queue
    self.threadName=threadName

    def run(self):
        while True:
            #grabs host from queue
            row = self.queue.get()
            print("thread %s processing row"%(self.threadName))
            processImage(row)
            #signals to queue job is done
            self.queue.task_done()

start = time.time()

def populate_queue():
    db = sqlite3.connect("data/images.sqlite")
    db.row_factory=sqlite3.Row
    c = db.cursor()
    year, month, imageDir="","",""
    timestamp=parse("1933-02-02").date()
    for row in c.execute("select * from images  order by CREATEDATE desc"):
        sourceFile=row[4]
        correctedDate=re.sub(r'(\d{4}):(\d{2}):(\d{2}\s+\d{2}:\d{2}:\d{2}).*',r'\1-\2-\3', row[0])
        try:
            parsedDate=parse(correctedDate)
        except:
            continue
        if  (parsedDate.year!=year or parsedDate.month!=month):
            year=parsedDate.year
            month=parsedDate.month
            imageDir="images_original/%s/%s"%(year, month)
            try:
                os.makedirs(imageDir)
            except:
                continue

        delta= relativedelta( timestamp,parsedDate)
        if(delta.years==0 and delta.months==0 and delta.days==0 and delta.hours==0 and delta.minutes<5):
            continue
        queue.put(row)
        print(correctedDate)
        timestamp=parsedDate
    db.close()

def main():
    populate_queue()
    
    #spawn a pool of threads, and pass them queue instance 
    for i in range(10):
        t = ThreadUrl(queue, i)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for host in hosts:
        queue.put(host)
    
    #wait on the queue until everything has been processed
    queue.join()
main()
print("Elapsed Time: %s" % (time.time() - start))


