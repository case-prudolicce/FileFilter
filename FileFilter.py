#!/bin/python
import re
import hashlib
import os
import sys

#function to make hash from files, which is read by blocks to avoid overloading ram
def md5_from_file(f,bs=2**20):
	h = hashlib.md5()
	while True:
		data = file.read(bs)
		if not data:
			break
		h.update(data)
	return h.hexdigest()

#Check if we have 4 args (4th arg will be sort_table)
#if not len(sys.argv) == 4:
#	sys.exit()

#Check if we have 3 args (Filefilter.py, Folder to filter, Folder to compare against)
if not len(sys.argv) == 3:
	sys.exit()

#Get first and second arguments (for target and comparison folder)
Target = sys.argv[1]
Destination = sys.argv[2]

#check if the .hashes exist, if it does prompt user to use it or overwrite it
Destination = os.path.abspath(Destination)
m = re.search('^(.*/.*/).*$',Destination)
hs = m.group(1)
if os.path.isfile(hs+".hashes"):
	v = input(hs+".hashes Already exists. Do you want to use it instead of overwriting it (Y/n)?")
	if v == "n": #Overwritting, same as writting
		hashes = open(hs+".hashes",'a')
		
		for sd,d,f in os.walk(Destination):
			for filename in f:
				filepath = sd + os.sep + filename
				print(filepath)
				file = open(filepath,mode='rb')
				h = md5_from_file(file)+"\n"
				file.close()
				hashes.write(h)
		hashes.close()
	
else: #Writting
#Open a file named .hashes in the folder directly outside of Destination
	hashes = open(hs+".hashes",'a')
	
#Open all files in Destination (Files to compare targets against)
	for sd,d,f in os.walk(Destination):
		for filename in f:
			filepath = sd + os.sep + filename
			print(filepath)
			file = open(filepath,mode='rb')
			#Add 
			h = md5_from_file(file)+"\n"
			file.close()
#For each file, make a hash of it and write it in .hashes
			hashes.write(h)
	hashes.close()


#Reopen (or open if chose yes) hashes in read mode
#Get all hashes from files, removes trailing newline and store in a data structure (list for now)
hashlist = []
with open(hs+".hashes",'r') as hashes:
	h4sh = hashes.readline()
	c = 1
	while h4sh:
		#print(h4sh[:-1])
		hashlist.append(h4sh[:-1])
		h4sh = hashes.readline()
		c += 1

#Open sorttable from $HOME/.config/filefilter/sort_table from the third argument
#make sort dictionary

#Open all file in Target (Files to check/remove) 
#For each file, make a hash of it and compare it against .hashes
for sd,d,f in os.walk(Target):
	for filename in f:
		filepath = sd + os.sep + filename
		file = open(filepath,mode='rb')
		#Add 
		h = md5_from_file(file)
		for comp in hashlist:
#If theres a match, remove that file
			if h == comp:
				print("DUPLICATE DETECTED: " + filepath + "... Removing")
				os.remove(filepath)
				break
			else:
				pass #This will sort the file based on fileinfo
#Otherwise, get file info
#sort it based on sort_table
		file.close()
