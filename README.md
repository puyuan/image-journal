image-journal
=============
Ever wanted to clean up duplicate photos in your hard drive and folders, but don't want to do it manually. This tool
automatically clean up your image folder and deletes duplicate photos, while preserving the best copy (by resolution). 

Ever wanted to see a timeline of your photos without having to organize all your photos. This tool creates a photo album
and selects representative photos based on timestamp. It shows a summary of all your photos without any clutter and manual 
organization.  e.g. if you taken tons of photos in succession in a short time frame, only a representative will be selected, which is good enough
if you are lazy to organize photos.  


tools/cleanPictures.sh  path_to_folder
- Clean image folder by removing all duplicate images with the same creation timestamps. 
The largest resolution photo will be kept, while all others will be deleted

createImageAlbum.sh 
- creates a new photo album from image folder. This will retrieve exif info from each folder. 

tools/quickCopy.sh
- copy any new images into existing photo album. This operation will be quicker than createImageAlbum.sh, which creates
album from scratch. Use quickCopy when adding new photos to the album. 

Web Presentation:
- gallery.html - Show's a timeline of all photos in your album by selecting representative photos for each timeframe. i.e. if you
take successive photos within a short time frame, only one will be shown. The selection is done automatically. 
