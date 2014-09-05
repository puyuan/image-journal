exiftool  -r -n -json ~/Pictures/ > images.json
rm images.sqlite
python createdb.py
python querydb.py
