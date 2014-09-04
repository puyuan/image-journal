exiftool -r -CREATEDATE -IMAGEHEIGHT  -csv .  > filelist.txt
sort -t, -k3n filelist.txt > filelist_sort_by_size
sort -t, -k2 filelist_sort_by_size  | cut -d, -f2 | uniq -c > unique.txt
python compare.py
