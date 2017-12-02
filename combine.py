from PIL import Image, ExifTags
import os.path

from dateutil import parser
import json
import os
journal = json.load(open("journal.json","r"))

gallery_f = open("gallery.json", "r")

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

for item in journal["entries"]:
    for image_str in gallery_f:
        image = json.loads(image_str)
        if item["date"]+"T"+item["time"] <= image["timestamp"]:
            timestamp = parser.parse(image["timestamp"]).strftime('%d%b%Y%H')
            item["url"] = "images/%s.jpg" % timestamp
            outfile = "images/%s.jpg"%timestamp
            if not os.path.isfile(outfile):
                im = Image.open(image["path"])
                im = rotate_image(im)
                size=(600,600)
                im.thumbnail(size, Image.LANCZOS)
                im.save(outfile, "JPEG", quality=90)
            break
f= open("journal_data.json", 'w')
f.write("var journal_data = ")
json.dump(journal, f )
