echo "Fetching Exif info from all photos"
exiftool   -r -n -json ~/Pictures/ > data/images.json
echo "Cleaning previous sqlite DB"
rm data/images.sqlite
echo "Creating database..."
python createdb.py
echo "Creating Json File"
python querydb.py
echo "Create Album Complete"
exit 0
