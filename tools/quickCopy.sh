#!/bin/bash
source env.sh
python convertJsonImage.py > $data/tmp_filelist.txt
#cut -d, -f1 $data/filelist.txt > $data/tmp_filelist.txt
find /home/puyuan/Pictures -iname *.jpg  > $data/tmp_sourceFileList.txt
grep -F -x -v -f $data/tmp_filelist.txt $data/tmp_sourceFileList.txt > $data/tmp_new_files.txt
python quickcopy.py
cd ../; python querydb.py
