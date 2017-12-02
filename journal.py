#from PIL import Image, ExifTags
import os.path
import os
from dateutil.parser import parse
from datetime import timedelta
import json

from gallery import get_images

def get_journal():
    cmd = "jrnl  --export json"
    strresult = os.popen(cmd).read()
    result = json.loads(strresult)
    return result

"""
def rotate_image(image):
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation]=='Orientation':
            break
    exif=dict(image._getexif().items())
    print(exif[orientation])

    if exif[orientation] == 3:
        image=image.rotate(180, expand=True)
    elif exif[orientation] == 6:
        image=image.rotate(270, expand=True)
    elif exif[orientation] == 8:
        image=image.rotate(90, expand=True)
    return image
"""

def get_combined_journal():
    journal = get_journal()
    images = get_images()
    entries = journal["entries"]
    len_journal = len(entries)
    len_images = len(images)
    i = len_journal - 1
    j = 0

    while i >=  0 and j < len_images:
        entry = entries[i]
        image = images[j]
        entry_timestamp = parse(entry["date"]+"T"+entry["time"])
        image_create_timestamp = parse(image["CreateDate"])

        if image_create_timestamp < entry_timestamp - timedelta(hours=3):
            i -= 1
        elif image_create_timestamp > entry_timestamp:
            j += 1
        else:
            entry["url"] = image["thumb"]
            i -= 1

    return journal


