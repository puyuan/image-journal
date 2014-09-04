import sqlite3
import os
import json
import hashlib

def retrieveVal(dic, key):
	if(dic.has_key(key)):
		return dic[key]
	else:
		return "" 

db = sqlite3.connect("images.sqlite")
c = db.cursor()

#c.execute('''create table images
#         (CreateDate text primary key,
#	  GPSLatitude real,
#	GPSLongitude   real, 
#	GPSAltitude    real ,
#	SourceFile   text
#          )''')


images=json.load(open("images.json"))
for image in images:
#	for k,v in image.iteritems():
#		print k=="CreateDate"
	createDate=retrieveVal(image, "CreateDate")
	gpsLatitude=retrieveVal(image, "GPSLatitude")
	gpsLongitude=retrieveVal(image, "GPSLongitude")
	gpsAltitude=retrieveVal(image, "GPSAltitude")
	sourceFile=retrieveVal(image, "SourceFile")
	md5sum=hashlib.md5(sourceFile.encode('utf-8')).hexdigest()
	#os.system("exiftool -b -ThumbnailImage '%s' > images/%s_t.jpg" %(sourceFile, md5sum ))
        if (not os.path.isfile("images/%s_t.jpg"%md5sum)):
            os.system("convert  -auto-orient -thumbnail x200 '%s'  images/%s_t.jpg" %(sourceFile, md5sum ))
        if (not os.path.isfile("images_original/%s.jpg"%md5sum)):
            os.system("convert   -resize 606x400^ -gravity center  -crop 606x400+0+0  -strip -auto-orient -quality 86 '%s'  images_original/%s.jpg" %(sourceFile, md5sum ))
        print md5sum
	columns=(createDate, gpsLatitude, gpsLongitude, gpsAltitude, sourceFile)
	print columns
	try:
                print "executing"
		c.execute("insert into images values (?, ?, ? ,?, ?)", columns)
	except:
		"failed"

db.commit()
db.close()
	#c.execute()


