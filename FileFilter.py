#!/bin/python
import re
import hashlib
import os
import sys
import argparse
import magic

#function to make hash from files, which is read by blocks to avoid overloading ram
def md5_from_file(f,bs=2**20):
	h = hashlib.md5()
	while True:
		data = f.read(bs)
		if not data:
			break
		h.update(data)
	return h.hexdigest()

#Function to create and write .hashes
def make_hashfile(f, d):
	pass
	if os.path.isfile(f):
		v = input(f+" Already exists. Do you want to use it instead of overwriting it (Y/n)?")
		if v == "n": #Overwritting, same as writting
			hashes = open(f,'w')
			
			for sd,d,F in os.walk(d):
				for filename in F:
					filepath = sd + os.sep + filename
					#print(filepath)
					file = open(filepath,mode='rb')
					h = md5_from_file(file)+"\n"
					file.close()
					hashes.write(h)
			hashes.close()
		
	else: #Writting
	#Open a file named .hashes in the folder directly outside of Destination
		hashes = open(f,'w')
		
	#Open all files in Destination (Files to compare targets against)
		for sd,d,F in os.walk(d):
			for filename in F:
				filepath = sd + os.sep + filename
				#print(filepath)
				file = open(filepath,mode='rb')
				#Add 
				h = md5_from_file(file)+"\n"
				file.close()
	#For each file, make a hash of it and write it in .hashes
				hashes.write(h)
		hashes.close()

#Function to moves a file to destination
def move_file(f,d):
	#print(f,"->",os.path.basename(f),"->",d+os.path.basename(f))
	os.rename(f,d+os.path.basename(f))
	return d+os.path.basename(f)

#Function to sorts the files to Sort_Dest based on Sort_Loc
def sort_files(ts,sl,sd):
	sl = os.path.abspath(sl)
	
	sd = os.path.abspath(sd)
	if os.path.isfile(sl):
		table = {}
		with open(sl,'r') as stable:
			entry = stable.readline()
			c = 1
			while entry:
				if not ( entry[:-1] == "" or entry[0] == "#"):
					table[entry[:-1].split(':')[0]] = entry[:-1].split(':')[1]
				entry = stable.readline()
				c += 1
	
	for file in ts:
		mime = magic.from_file(file, mime=True)
		moved = False
		for mt in table.keys():
			if mime == mt:
				move_file(file,sd+table[mime])
				moved = True
		if not moved:
			n = move_file(file,sd+table['*'])

#Configure argparser
parser = argparse.ArgumentParser()
parser.add_argument('target')
parser.add_argument('-d','--destination')
parser.add_argument('-H','--hashes')
parser.add_argument('-s','--sort-loc')
parser.add_argument('-S','--sort-dest')
parser.add_argument('--no-sort',action='store_true')
args = parser.parse_args()

Target = args.target
if args.destination == None and args.hashes == None:
	print("You either need -d or -H")
	sys.exit()

if args.sort_loc == None:
	#Default
	#Sort_Loc == "default value"
	Sort_Loc = "/usr/share/FileFilter/default_sort_table"
	print(Sort_Loc)
else:
	Sort_Loc = args.sort_loc

#Check if hashes hasn't been defined, if it didnt, make one outside destination
if args.hashes == None:
	Destination = os.path.abspath(args.destination)
	m = re.search('^(.*/.*/).*$',Destination)
	Hashes = m.group(1)+".hashes"
	make_hashfile(Hashes,Destination)
else:
	Hashes = os.path.abspath(args.hashes)
	m = re.search('^(.*/.*/).*$',Hashes)
	Destination = m.group(1)
	make_hashfile(Hashes,args.destination)

#Sets Sort_Dest (Needed after Destination is defined) to -S or outside destination
if args.sort_dest == None:
	Sort_Dest = os.path.abspath(Destination)
	m = re.search('^(.*/.*/).*$',Destination)
	Sort_Dest = m.group(1)+"Sorted/"
else:
	Sort_Dest = args.sort_dest

#Open hashes in read mode, get all hashes from files, removes trailing newline and stores them in a list
hashlist = []
with open(Hashes,'r') as hashes:
	h4sh = hashes.readline()
	c = 1
	while h4sh:
		hashlist.append(h4sh[:-1])
		h4sh = hashes.readline()
		c += 1

#Open all file in Target 
#For each file, make a hash of it and compare it against the hash list
to_sort = []
for sd,d,F in os.walk(Target):
	for filename in F:
		filepath = sd + os.sep + filename
		file = open(filepath,mode='rb')
		h = md5_from_file(file)
		found = False
		for comp in hashlist:
			#If theres a match, remove that file
			if h == comp:
				os.remove(filepath)
				found = True
				break
			
		if not found:
			#Otherwise, get Add to the to_sort array
			to_sort.append(filepath)
		file.close()

#Sort using Sort_Loc to Sort_Dest is --no-sort isn't specified
if not (args.no_sort):
	sort_files(to_sort,Sort_Loc,Sort_Dest)
