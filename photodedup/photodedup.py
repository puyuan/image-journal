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
    tags=["ImageWidth", "ImageHeight", "SourceFile","CreateDate", "GPSLatitude", "GPSLongitude", "GPSAltitude"]
    with exiftool.ExifTool() as et:
        for root, dirs, files in os.walk("/mnt/hgfs/pictures"):
            fileList = [join(root, f) for f in files if ".jpg" in f.lower()]
            try:
                yield et.get_tags_batch(tags, fileList)
            except:
                 logger.warn("exiftool fail")


class PhotoIndex():
    def __init__(self):
        self.db=sqlite3.connect("images.sqlite")

    def insert_index(self):
        c = self.db.cursor()
        for metadataList in get_metadata_batch():


            columns= [(d.get("EXIF:CreateDate", ""),
                       d.get("EXIF:GPSLatitude", ""),
                       d.get("EXIF:GPSLongitude", ""),
                       d.get("EXIF:GPSAltitude", ""),
                       d.get("SourceFile", "")
                    #   d.get("File:ImageWidth", ""),
                    #   d.get("File:ImageHeight", "")
                       )for d in metadataList]

            for metadata in metadataList:
                logger.info("inserting %s", metadata.get('SourceFile', ""))

            c.executemany("insert or ignore into images values (?, ?, ? ,?, ?)", columns)
            self.db.commit()



           # except:
             #   logger.debug("Unexpected error: %s", sys.exc_info()[0])
             #   logger.warn("sqlite insert error")

    def create_index(self):
        c = self.db.cursor()
        c.execute('''create table if not exists images
                 (CreateDate text primary key,
              GPSLatitude real,
        GPSLongitude   real,
            GPSAltitude    real ,
            SourceFile   text
                  )''')

photoIndex=PhotoIndex()
photoIndex.create_index()
photoIndex.insert_index()
