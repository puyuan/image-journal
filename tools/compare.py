import os
f=open("unique.txt", "r")

filecount={}

for line in f:
	arr=line.split()
	if len(arr)<3:
		continue
	count=arr[0]
	date=arr[1]
	time=arr[2]
	filecount[date+" "+time]=int(count)

#for k, v in filecount.items(): 
#	print k, v


f=open("filelist_sort_by_size", "r")
for line in f:
	arr=line.split(",")
	if len(arr)<2:
		continue
	file_path=arr[0]
	datetime=arr[1].strip()
	if(filecount.has_key(datetime) and filecount[datetime]>1):
		print file_path
		try:
			os.remove(file_path)
		except:
			print "file doesn't exist, perhaps deleted already?"
		filecount[datetime]-=1
	
	
