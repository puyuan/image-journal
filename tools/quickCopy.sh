cut -d, -f1 filelist.txt > tmp_filelist.txt
find /home/puyuan/Pictures -iname *.jpg  > tmp_sourceFileList.txt
grep -F -x -v -f tmp_filelist.txt tmp_sourceFileList.txt > tmp_new_files.txt
