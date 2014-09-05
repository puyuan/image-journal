import sqlite3
import os
import json
import hashlib
from dateutil.parser import parse
from dateutil.relativedelta import *
from math import ceil
import re
def retrieveVal(dic, key):
	if(dic.has_key(key)):
		return dic[key]
	else:
		return "" 

def week_of_month(dt):
    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))

db = sqlite3.connect("images.sqlite")
db.row_factory=sqlite3.Row
c = db.cursor()

html="<html><body>"
month=''
year=''
timestamp=parse("1933-02-02").date()
f=open("gallery.json", "w")
images=[]
for row in c.execute("select * from images order by CREATEDATE desc"):
	sourceFile=row[4]
	md5sum=hashlib.md5(sourceFile.encode('utf-8')).hexdigest()
        #print row[0]
        correctedDate=re.sub(r'(\d{4}):(\d+):(.*)',r'\1-\2-\3', row[0])
        parsedDate=parse(correctedDate)
	if  (parsedDate.year!=year or parsedDate.month!=month):
		year=parsedDate.year
		month=parsedDate.month
		html+="<h3>%s/%s</h3>"%(year, month)
	delta= relativedelta( timestamp,parsedDate)
#	print delta.years, delta.months,  delta.days, delta.hours
#	print timestamp
#	print parsedDate
	if(delta.years==0 and delta.months==0 and delta.days==0 and delta.hours==0):
            pass
	else:
		timestamp=parsedDate
		html+= "<img src='images/%s.jpg'></img><br/>"%(md5sum)
                dic=dict(row)
                dic["thumb"]="images/%s_t.jpg"%md5sum
                dic["src"]="images_original/%s.jpg"%md5sum
                dic["group"]="%d-%d"%(parsedDate.year,parsedDate.month)
                dic["date"]=parsedDate.date().isoformat()
                #dic["group"]="%d-%d-%d"%(parsedDate.year,parsedDate.month,week_of_month(parsedDate))
                images.append(dic)

html+="</body></html>"
f.write("gallery_images="+json.dumps(images))

db.close()


