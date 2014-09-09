source env.sh
# remove pictures previously looked at
find "$image_folder"  -iname *.jpg -or -iname *.jpeg > $data/tmp_sourceFileList.txt
grep -F -x -v -f $data/tmp_checked_filelist.txt $data/tmp_sourceFileList.txt > $data/unchecked_files
cat $data/unchecked_files | shuf -n20 > $data/random_list
feh   --auto-zoom --geometry 1600x1200  -f  $data/random_list 
cat $data/random_list >> $data/tmp_checked_filelist.txt
