import itertools
import os
from os.path import join
import exiftool
import sqlite3
import sys
import logging
from logging.config import fileConfig

fileConfig('logging_config.ini')
logger = logging.getLogger()
logger.debug('often makes a very good meal of %s', 'visiting tourists')



def get_metadata_batch():
    tags=["ImageWidth", "ImageHeight", "SourceFile","CreateDate", "DateAcquired", "GPSLatitude", "GPSLongitude", "GPSAltitude"]
    with exiftool.ExifTool() as et:
        for root, dirs, files in os.walk("/mnt/hgfs/pictures"):
            fileList = [join(root, f) for f in files if ".jpg" in f.lower()]
            try:
                yield et.get_tags_batch(tags, fileList)
            except:
                 logger.warn("exiftool fail")


class PhotoIndex():
    def __init__(self, image_folder_path):
        self.db=sqlite3.connect("images.sqlite")
        self.image_folder_path=image_folder_path

    def insert_index(self):
        c = self.db.cursor()
        for metadataList in get_metadata_batch():


            columns= [(d.get("EXIF:CreateDate", d.get("DateAcquired","")),
                        d.get("EXIF:CreateDate", ""),
                       d.get("EXIF:GPSLatitude", ""),
                       d.get("EXIF:GPSLongitude", ""),
                       d.get("EXIF:GPSAltitude", ""),
                       d.get("SourceFile", "")
                    #   d.get("File:ImageWidth", ""),
                    #   d.get("File:ImageHeight", "")
                       )for d in metadataList]

            for metadata in metadataList:
                logger.info("inserting %s", metadata.get('SourceFile', ""))

            c.executemany("insert or ignore into images values (?, ?, ? ,?, ?, ?)", columns)
            self.db.commit()



           # except:
             #   logger.debug("Unexpected error: %s", sys.exc_info()[0])
             #   logger.warn("sqlite insert error")

    def create_index(self):
        c = self.db.cursor()
        c.execute('''create table if not exists images
                 (timestamp text primary key,
                 CreateDate text,
              GPSLatitude real,
        GPSLongitude   real,
            GPSAltitude    real ,
            SourceFile   text
                  )''')

    def dumpDB(self):
        logger.info("Get all images in index")
        c=self.db.cursor()
        file=open("/tmp/sqlite_files.log", "w")
        for (sourceFile,) in c.execute("select SourceFile from images order by SourceFile"):
            file.write(sourceFile+"\n")
        file.close()

    def dumpImageFolder(self):
        logger.info("Get all images in image folder")
        outfile = open("/tmp/imagefolder_files.log", "w")
        for root, dirs, files in os.walk(self.image_folder_path):
            dirs.sort()
            files.sort()
            for file in files:
                if ".jpg" in file.lower():
                    fullpath=join(root, file)
                    outfile.write(fullpath + "\n")
        outfile.close()

    def fetchNewImage(self):
        logger.info("Fetching new images")
        with open('/tmp/imagefolder_files.log')  as f, open('/tmp/sqlite_files.log') as f2:
            lines1 = set(map(str.rstrip, f))
            print(lines1.difference(map(str.rstrip, f2)))



photoIndex=PhotoIndex("/mnt/hgfs/pictures")
photoIndex.create_index()
photoIndex.dumpDB()
photoIndex.dumpImageFolder()
photoIndex.fetchNewImage()
photoIndex.insert_index()
