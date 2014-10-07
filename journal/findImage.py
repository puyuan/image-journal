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
    
    date = parse(date)
    date=date.replace(tzinfo=None)
    date=date.isoformat()

    print date
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
	return None

    return closestDate(imageList, date)["CREATEDATE"]

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
        print low, high, middle
        if (abs(low-high)<=1):
            return minDate(imageList, low, high, date)
        createDate=imageList[middle]["CREATEDATE"].replace(":", "-", 2).replace(" ", "T", 1)
	print createDate, date

        if(date < createDate):
            return recurse(imageList, low, middle, middle, date);
        else:
            return recurse(imageList, middle, high, middle,  date);

def minDate(imageList, dateAIndex, dateBIndex, targetDate):
    dateA=imageList[dateAIndex]["CREATEDATE"].replace(":", "-", 2).replace(" ", "T", 1)
    dateB=imageList[dateBIndex]["CREATEDATE"].replace(":", "-", 2).replace(" ", "T", 1)
    dateA=parse(dateA)
    dateB=parse(dateB)
    targetDate=parse(targetDate)
    deltaA=dateA-targetDate
    deltaB=dateB-targetDate
    if(abs(deltaA)>abs(deltaB)):
        return dateBIndex

    return dateAIndex


print findImage("2014-09-14T10:28:00")

