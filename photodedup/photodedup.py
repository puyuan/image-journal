#!/usr/bin/env python
# Paul Yuan 2016
import os
import sys
import argparse
import exiftool
import sqlite3
import logging
import tempfile
import exifread
import itertools
from logging.config import fileConfig
from os.path import join
import shutil


fileConfig('logging_config.ini')
logger = logging.getLogger()

class PhotoIndex():
    def __init__(self, image_folder_path):
        self.db=sqlite3.connect("images.sqlite")
        self.image_folder_path=image_folder_path

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

    def insert_images(self, new_images):
        c = self.db.cursor()
        for metadataList in self.__exifread_get_metadata(new_images):
		
            columns= [(d.get("EXIF:CreateDate", d.get("File:FileModifyDate","")),
                       d.get("EXIF:CreateDate", ""),
                       d.get("EXIF:GPSLatitude", ""),
                       d.get("EXIF:GPSLongitude", ""),
                       d.get("EXIF:GPSAltitude", ""),
                       d.get("SourceFile", "")
                       )for d in metadataList]

            for metadata in metadataList:
                logger.info("inserting %s", metadata.get('SourceFile', ""))
                logger.debug(metadata)

            c.executemany("insert or ignore into images values (?, ?, ? ,?, ?, ?)", columns)
            self.db.commit()

    def insert_exifread_images(self, new_images):
        c = self.db.cursor()
        count=0
        for metadataList in split_every(3000,self.__exifread_get_metadata(new_images)):

            columns = [(str(d.get("EXIF DateTimeOriginal", d.get("Image DateTime", ""))),
                        str(d.get("EXIF DateTimeOriginal", "")),
                        str(d.get("GPS GPSLatitude", "")),
                        str(d.get("GPS GPSLongitude", "")),
                        str(d.get("GPS GPSAltitude", "")),
                        unicode(d.get("SourceFile", ""), "utf-8")
                        ) for d in metadataList]

            count+=len(columns)
            logger.info("Processed %d images..." % count )

            for metadata in metadataList:
                logger.debug("inserting %s", metadata.get("SourceFile", ""))


            c.executemany("insert or ignore into images values (?, ?, ? ,?, ?, ?)", columns)
            self.db.commit()


    def fetch_new_images(self):
        logger.info("Fetching new images")
        dbfile=self.__dumpDB()
        folderfile=self.__dumpImageFolder()
        logger.debug(folderfile)
        logger.debug(dbfile)
        with open(dbfile)  as a, open(folderfile) as b:
          #  lines1 = set(map(str.rstrip, f))
          #  return lines1.difference(map(str.rstrip, f2))
          done = object()
          aNext = next(a, done)
          bNext = next(b, done)

          while (aNext is not done) and (bNext is not done):
              if (aNext > bNext):
                  yield bNext.rstrip()
                  bNext = next(b, done)
              elif (aNext < bNext):
                  aNext=next(a, done)
              else: # equals
                  bNext = next(b, done)
                  aNext = next(a, done)

          while bNext is not done:
            yield bNext.rstrip()
            bNext = next(b, done)



    def check_new_images(self):
        logger.info("checking new images")

        fileList=[image for image in self.fetch_new_images()]
        if not fileList:
            logger.info("list is empty")
            return False

        logger.info("List is not empty, following files are left:")
        for file in fileList:
            logger.info(file)
        return True

    def print_new_images_count(self):
        logger.info("Estimated new images: %d", self.get_new_images_count())

    def get_new_images_count(self):
        logger.info("checking new images")

        count=0
        for image in self.fetch_new_images():
            count+=1
        return count





    def remove_images(self, duplicate_images):
      for file in duplicate_images:
          os.remove(file)

    def copy_duplicates(self):
      self.insert_new_images()
      count=0
      for file in self.fetch_new_images():
          count+=1
          shutil.copy(file, '/tmp/test/%d.jpg'%(count))


		  
    def __get_images_metadata(self, images):
        tags=["ImageWidth", "ImageHeight", "SourceFile","CreateDate",
			  "FileModifyDate", "GPSLatitude", "GPSLongitude", "GPSAltitude"]

        with exiftool.ExifTool() as et:
            fileList = []
            count = 0
            for filename in images:
                fileList.append(filename)
                logger.info('Extracting metadata for: %s', filename)
                count += 1
                if (count % 1000 == 0):
                    try:
                        logger.info("Processing with ExifTool. \n Please wait..")
                        yield et.get_tags_batch(tags, fileList)

                    except Exception as ex:
                        logging.exception("exiftool could not process, perhaps folder is empty?")

                    fileList=[]
            # process remaining list
            if fileList:
                try:
                    yield et.get_tags_batch(tags, fileList)
                except:
                    logger.warn("exiftool could not process, perhaps folder is empty?")
    def __exifread_get_metadata(self, images):
        for filename in images:
            f=open(filename)
            tags = exifread.process_file(f, details=False)
            tags["SourceFile"]=filename
            yield tags
            f.close()

    def __dumpDB(self):
        logger.info("Get all images in index")
        c = self.db.cursor()
        file = tempfile.NamedTemporaryFile(delete=False)
        for (sourceFile,) in c.execute("select SourceFile from images order by SourceFile"):
            file.write(sourceFile.encode('utf-8') + "\n")
        file.close()
        return file.name

    def __dumpImageFolder(self):
        logger.info("Get all images in image folder")
        outfile = tempfile.NamedTemporaryFile(delete=False)
        for root, dirs, files in os.walk(self.image_folder_path):
            dirs.sort()
            files.sort()
            for file in files:
                
                if ".jpg" in file.lower():
                    fullpath=join(root, file)
                    outfile.write(fullpath + "\n")
        outfile.close()
        return outfile.name

def split_every(n, iterable):
    i = iter(iterable)
    piece = list(itertools.islice(i, n))
    while piece:
        yield piece
        piece = list(itertools.islice(i, n))

# TODO
def get_parser():
    parser = argparse.ArgumentParser(description='photo deduplication tool')
    parser.add_argument('query', metavar='QUERY', type=str, nargs='*',
                        help='the question to answer')
    parser.add_argument('-p', '--pos', help='select answer in specified position (default: 1)', default=1, type=int)
    parser.add_argument('-a', '--all', help='display the full text of the answer',
                        action='store_true')
    parser.add_argument('-l', '--link', help='display only the answer link',
                        action='store_true')
    parser.add_argument('-c', '--color', help='enable colorized output',
                        action='store_true')
    parser.add_argument('-n', '--num-answers', help='number of answers to return', default=1, type=int)
    parser.add_argument('-C', '--clear-cache', help='clear the cache',
                        action='store_true')
    parser.add_argument('-v', '--version', help='displays the current version of photodedup',
                        action='store_true')
    return parser
               

image_path="/cygdrive/f/cleaned_Photos"
photoIndex=PhotoIndex(image_path)
photoIndex.create_index()
photoIndex.print_new_images_count()
new_images=photoIndex.fetch_new_images()
photoIndex.insert_exifread_images(new_images)
photoIndex.check_new_images()

