import sqlite3
import os
import json
from datetime import timedelta, datetime
from dateutil.parser import parse
from dateutil import relativedelta
from math import ceil
import re
import hashlib
import logging

PHOTO_INDEX_PATH = os.path.join(os.path.expanduser("~"), ".photoindex", "images.sqlite")



def configure_logger():
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    return logger

logger = configure_logger()

def connect_database():
    db = sqlite3.connect(PHOTO_INDEX_PATH)
    db.row_factory=sqlite3.Row
    return  db

def gen_html():
    pass

def gen_gallery_file():
    gallery_file = open("static/gallery.json", "w")


def get_images():
    print("loading sqlite file...")
    month=''
    year=''
    current_timestamp= datetime(1933,2, 1)
    images=[]

    with connect_database() as db:
        c = db.cursor()
        for row in c.execute("select * from images  order by CREATEDATE desc"):
            row_dic = dict(row)

            # Correct Date Format
            try:
                correctedDate = re.sub(r'(\d{4}):(\d{2}):(\d{2}\s+\d{2}:\d{2}:\d{2}).*', r'\1-\2-\3', row_dic["CreateDate"])
                parsedDate=parse(correctedDate)
                row_dic["CreateDate"] = parsedDate.isoformat()
            except:
                continue


            time_diff= current_timestamp - parsedDate
            if abs(time_diff.total_seconds()) < 300 :
                continue
            else:
                photo_timestamp = parsedDate.strftime("%s")
                row_dic["thumb"] = "static/images/%s_t.jpg" % photo_timestamp
                row_dic["group"] = "%d-%d"%(parsedDate.year,parsedDate.month)
                row_dic["date"] = parsedDate.date().isoformat()
                images.append(row_dic)
                sourceFile = row_dic["SourceFile"]
                if (not os.path.isfile("static/images/%s_t.jpg"%photo_timestamp)):
                    cmd = "convert -auto-orient -thumbnail x300 \"%s\" static/images/%s_t.jpg" % (sourceFile, photo_timestamp)
                    logger.info("Converting file \n %s", cmd)
                    os.system(cmd)
                current_timestamp = parsedDate


    return images

if __name__ == "__main__":
    get_images()

