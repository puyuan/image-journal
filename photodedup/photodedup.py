#!/usr/bin/env python
# Paul Yuan 2016
import os
import sys
import argparse
import sqlite3
import logging
import exifread
import itertools

from logging.config import fileConfig
from os.path import join
import shutil


fileConfig('logging_config.ini')
logger = logging.getLogger()

class PhotoIndex():
    def __init__(self, image_folder_path):
        self.conn=sqlite3.connect("images.sqlite")
        self.image_folder_path=image_folder_path

    def create_index(self):
        logger.info("Create index if not exists")
        cur = self.conn.cursor()
        cur.execute('''create table if not exists images
				 (timestamp text primary key,
				  CreateDate text,
				  GPSLatitude real,
				  GPSLongitude   real,
				  GPSAltitude    real ,
				  SourceFile   text
				  )''')



    def insert_images(self, new_images):
        cur = self.conn.cursor()
        count=0
        for metadataList in split_every(1000, self.__get_images_metadata(new_images)):

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


            cur.executemany("insert or ignore into images values (?, ?, ? ,?, ?, ?)", columns)
            self.conn.commit()


    def get_new_images(self):
        logger.info("Fetching new images")
        dbImages=self.__get_db_images()
        folderImages=self.__get_folder_images()

        # use sorted iterator to find new images
        done = object()
        dbNext = next(dbImages, done)
        folderNext = next(folderImages, done)

        while (dbNext is not done) and (folderNext is not done):
          logger.debug("dbNext: %s, folderNext %s"%(dbNext, folderNext))
          if (dbNext > folderNext):
              yield folderNext.rstrip()
              folderNext = next(folderImages, done)
          elif (dbNext < folderNext):
              dbNext=next(dbImages, done)
          else: # equals
              folderNext = next(folderImages, done)
              dbNext = next(dbImages, done)

        while folderNext is not done:
            logger.debug("dbNext: %s, folderNext %s" % (dbNext, folderNext))
            yield folderNext.rstrip()
            folderNext = next(folderImages, done)



    def check_new_images(self):
        logger.info("checking new images")

        fileList=[image for image in self.get_new_images()]
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
        for image in self.get_new_images():
            logger.debug("Counting image: %s"% image)
            count+=1
        return count





    def remove_images(self, duplicate_images):
      for file in duplicate_images:
          os.remove(file)

    def copy_duplicates(self):
      self.insert_new_images()
      count=0
      for file in self.get_new_images():
          count+=1
          shutil.copy(file, '/tmp/test/%d.jpg'%(count))


    def __get_images_metadata(self, images):
        for filename in images:
            f=open(filename)
            tags = exifread.process_file(f, details=False)
            tags["SourceFile"]=filename
            yield tags
            f.close()

    def __get_db_images(self):
        logger.info("Get all images in index")
        c = self.conn.cursor()

        for (sourceFile,) in c.execute("select SourceFile from images order by SourceFile"):
            yield sourceFile.encode('utf-8')



    def __get_folder_images(self):
        logger.info("Get all images in image folder")
        for root, dirs, files in os.walk(self.image_folder_path):
            dirs.sort()
            files.sort()
            for file in files:

                if ".jpg" in file.lower():
                    fullpath=join(root, file)
                    yield fullpath

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
new_images=photoIndex.get_new_images()
photoIndex.insert_images(new_images)
photoIndex.check_new_images()

