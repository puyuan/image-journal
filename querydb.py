import sqlite3
import os
import json
from datetime import timedelta, datetime
from dateutil.parser import parse
from dateutil import relativedelta
from math import ceil
import re
import hashlib


def retrieveval(dic, key):
    if(dic.has_key(key)):
        return dic[key]
    else:
        return ""


def week_of_month(dt):
    first_day = dt.replace(day=1)
    dom = dt.day
    adjusted_dom = dom + first_day.weekday()
    return int(ceil(adjusted_dom/7.0))

photoindex_path = os.path.join(os.path.expanduser("~"), ".photoindex", "images.sqlite")
db = sqlite3.connect(photoindex_path)
db.row_factory=sqlite3.Row
c = db.cursor()

print("loading sqlite file...")

html="<html><body>"
month=''
year=''
timestamp= datetime(1933,2, 1)
images=[]
imageDir="images_original"
gallery_file = open("static/gallery.json", "w")
IMAGE_DIR = "static/"

for row in c.execute("select * from images  order by CREATEDATE desc"):
    dic = dict(row)
    sourceFile = dic["SourceFile"]
    correctedDate=re.sub(r'(\d{4}):(\d{2}):(\d{2}\s+\d{2}:\d{2}:\d{2}).*',r'\1-\2-\3', dic["CreateDate"])
    print(correctedDate)
    try:
        parsedDate=parse(correctedDate)
        dic["CreateDate"] = parsedDate.isoformat()
    except:
        continue
    if  parsedDate.year != year or parsedDate.month != month:
        year = parsedDate.year
        month = parsedDate.month
        html += "<h3>%s/%s</h3>"%(year, month)
        imageDir = "static/images_original/%s/%s"%(year, month)
        try:
            os.makedirs(imageDir)
        except:
            continue
    photo_timestamp = parsedDate.strftime("%s")
    print(photo_timestamp)

    delta= timestamp - parsedDate
    print(parsedDate, timestamp)
    print(delta.days, delta.seconds)

    print(abs(delta.total_seconds()) < 300 )
    if abs(delta.total_seconds()) < 300 :
        continue
    else:
        html += "<img src='images/%s.jpg'></img><br/>"%(photo_timestamp)
        dic["thumb"] = "images/%s_t.jpg" % photo_timestamp
        dic["src"] = "images_wide/%s.jpg" % photo_timestamp
        dic["group"] = "%d-%d"%(parsedDate.year,parsedDate.month)
        dic["date"] = parsedDate.date().isoformat()
        images.append(dic)
        sourceFile = dic["SourceFile"]
        print(sourceFile, photo_timestamp)
        if (not os.path.isfile("static/images/%s_t.jpg"%photo_timestamp)):
            cmd = "convert -auto-orient -thumbnail x300 \"%s\" static/images/%s_t.jpg" % (sourceFile, photo_timestamp)
            print(cmd)
            os.system(cmd)
        #if (not os.path.isfile("%s/%s.jpg"%(imageDir, photo_timestamp))):
        #    os.system("convert  \"%s\" -channel rgb -auto-level  -resize 1920x1080^ -gravity center   -auto-orient -quality 86   %s/%s.jpg" % (sourceFile, imageDir, photo_timestamp))

        timestamp = parsedDate

html += "</body></html>"
gallery_file.write("gallery_images=" + json.dumps(images))

db.close()


