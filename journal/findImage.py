import sqlite3
import os
import json
import hashlib
from dateutil.parser import parse
from dateutil.relativedelta import *
from math import ceil
import re
import pdb


def findImage(date):
    db = sqlite3.connect("../data/images.sqlite")
    db.row_factory=sqlite3.Row
    c = db.cursor()
    dateFormat="%Y:%m:%d %H:%M:%S"
    startDate="strftime('%s', '%s' , '-30 minutes')"%(dateFormat, date)
    endDate="strftime('%s', '%s' , '+30 minutes')"%(dateFormat, date)

    imageList=[]

    for row in c.execute("select * from images where CREATEDATE > %s AND CREATEDATE< %s order by CREATEDATE "% (startDate, endDate)):
        if  row["CREATEDATE"].find("jumbo")>-1:
            continue
        imageList.append(row)
    db.close()
    if len(imageList)==0:
        return

    print closestDate(imageList, date)["CREATEDATE"]

def closestDate(imageList, date):
    if (len(imageList)==0):
        return None
    high=len(imageList)-1;
    low=0
    pdb.set_trace()
    imgIndex=recurse(imageList, low, high, 0,  date)
    return imageList[imgIndex]

def recurse(imageList, low, high, minimun, date):
        middle=int(ceil((low+high)/2.0))
        print low, high
        if (low >= high):
            return minimun
        createDate=imageList[middle]["CREATEDATE"].replace(":", "-", 2)

        if(date < createDate):
            return recurse(imageList, low, middle, middle, date);
        else:
            return recurse(imageList, middle+1, high, middle,  date);


findImage("2014-10-02 16:42:36+08:00")

