#!/bin/bash
set -x

if [ ! $# == 1 ]; then
    echo "Please provide the path to your images"
    exit
  fi

filepath=$1

exiftool -r -CREATEDATE -IMAGEHEIGHT  -csv $filepath  > filelist.txt
sort -t, -k3n filelist.txt > filelist_sort_by_size
#sort -t, -k2 filelist_sort_by_size  | cut -d, -f2 | uniq -c > unique.txt
python compare.py
