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



class PhotoIndex():
    def __init__(self, image_folder_path):
        self.db=sqlite3.connect("images.sqlite")
        self.image_folder_path=image_folder_path
		
    def __get_metadata_batch(self):
            tags=["ImageWidth", "ImageHeight", "SourceFile","CreateDate", "FileModifyDate", "GPSLatitude", "GPSLongitude", "GPSAltitude"]
            with exiftool.ExifTool() as et:
                    for root, dirs, files in os.walk(self.image_folder_path):
                            fileList = [join(root, f) for f in files if ".jpg" in f.lower()]
                            try:
                                    yield et.get_tags_batch(tags, fileList)
                            except:
                                     logger.warn("exiftool could not process, perhaps folder is empty?")

    def __get_new_images_metadata(self):
            tags=["ImageWidth", "ImageHeight", "SourceFile","CreateDate", "FileModifyDate", "GPSLatitude", "GPSLongitude", "GPSAltitude"]
            imagesIter=self.fetch_new_images()
            with exiftool.ExifTool() as et:
                        fileList=[]
                        count=0
                        for filename in imagesIter:
                            fileList.append(filename)
                            count+=1
                            if (count %1000==0):
                                try:
                                        logger.info("Running ExifTool")
                                        yield et.get_tags_batch(tags, fileList)
                                except:
                                         logger.warn("exiftool could not process, perhaps folder is empty?")
                        # process remaining list
                        if fileList:
                            try:
                                    yield et.get_tags_batch(tags, fileList)
                            except:
                                     logger.warn("exiftool could not process, perhaps folder is empty?")


    def insert_new_images(self):
        c = self.db.cursor()
        for metadataList in self.__get_new_images_metadata():


            columns= [(d.get("EXIF:CreateDate", d.get("File:FileModifyDate","")),
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
                logger.debug(metadata)

            c.executemany("insert or ignore into images values (?, ?, ? ,?, ?, ?)", columns)
            self.db.commit()



           # except:
             #   logger.debug("Unexpected error: %s", sys.exc_info()[0])
             #   logger.warn("sqlite insert error")

    def create_index(self):
        logger.info("Create table if not exists")
        c = self.db.cursor()
        c.execute('''create table if not exists images
                 (timestamp text primary key,
                 CreateDate text,
              GPSLatitude real,
        GPSLongitude   real,
            GPSAltitude    real ,
            SourceFile   text
                  )''')

    def __dumpDB(self):
        logger.info("Get all images in index")
        c=self.db.cursor()
        file=open("/tmp/sqlite_files.log", "w")
        for (sourceFile,) in c.execute("select SourceFile from images order by SourceFile"):
            file.write(sourceFile.encode('utf-8')+"\n")
        file.close()

    def __dumpImageFolder(self):
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

    def fetch_new_images(self):
        logger.info("Fetching new images")
	self.__dumpDB()
	self.__dumpImageFolder()

        with open('/tmp/imagefolder_files.log')  as f, open('/tmp/sqlite_files.log') as f2:
            lines1 = set(map(str.rstrip, f))
            return lines1.difference(map(str.rstrip, f2))

    def check_new_images(self):
        logger.info("checking new images")
        fileList=[image for image in self.fetch_new_images()]
        if not fileList:
            logger.info("list is empty")
            return False

        logger.info("List is not empty, following files are left:")
        for file in fileList:
            logger.info(file)

    def remove_duplicate(self):
      for file in self.fetch_new_images():
          os.remove(file)


               

image_path="/mnt/hgfs/Pictures"
photoIndex=PhotoIndex(image_path)
photoIndex.create_index()
photoIndex.insert_new_images()
photoIndex.check_new_images()
#photoIndex.remove_duplicate()
