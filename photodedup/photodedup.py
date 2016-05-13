#!/usr/bin/env python
# Paul Yuan 2016


import os
import sys
import argparse
import exiftool
import sqlite3
import logging
from logging.config import fileConfig
from os.path import join


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
        for metadataList in self.__get_new_images_metadata(new_images):
		
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
		return True

    def remove_images(self, duplicate_images):
      for file in duplicate_images:
          os.remove(file)
		  
	def __get_images_metadata(self, images):
		tags=["ImageWidth", "ImageHeight", "SourceFile","CreateDate", 
			  "FileModifyDate", "GPSLatitude", "GPSLongitude", "GPSAltitude"]

		with exiftool.ExifTool() as et:
			fileList=[]
			count=0
			for filename in images:
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
               

image_path="/mnt/hgfs/Pictures"
photoIndex=PhotoIndex(image_path)
photoIndex.create_index()
new_images=photoIndex.fetch_new_images()
photoIndex.insert_images(new_images)
remaining_images=photoIndex.fetch_new_images()
photoIndex.remove_duplicate(remaining_images)
