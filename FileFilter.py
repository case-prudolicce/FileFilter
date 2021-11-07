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
def make_hashfile(f, d, prompt=True,v=True):
	if os.path.isfile(f):
		if(prompt):
			v = False if input(f+" Already exists. Do you want to use it instead of overwriting it (Y/n)?") == "n" else v
		if v: #Overwritting, same as writting
			print("Making hashfile for "+d)
			hashes = open(f,'w')
			
			for sd,d,F in os.walk(d):
				for filename in F:
					filepath = sd + os.sep + filename
					file = open(filepath,mode='rb')
					h = md5_from_file(file)+"\n"
					file.close()
					hashes.write(h)
			hashes.close()	
	else:
		hashes = open(f,'w')
		#Open all files in Destination (Files to compare targets against)
		for sd,d,F in os.walk(d):
			#For each file, make a hash of it and write it in the hash list
			for filename in F:
				filepath = sd + os.sep + filename
				file = open(filepath,mode='rb')
				h = md5_from_file(file)+"\n"
				file.close()
				hashes.write(h)
		hashes.close()

#Function to moves a file to destination
def move_file(f,d):
	os.rename(f,d+os.path.basename(f))
	return d+os.path.basename(f)

#Function to sorts the files to Sort_Dest based on Sort_Loc
def sort_files(to_sort,sort_loc,sort_dest):
	sort_loc = os.path.abspath(sort_loc)
	
	sort_dest = os.path.abspath(sort_dest)
	if os.path.isfile(sort_loc):
		table = {}
		with open(sort_loc,'r') as stable:
			entry = stable.readline()
			c = 1
			while entry:
				if not ( entry[:-1] == "" or entry[0] == "#"):
					table[entry[:-1].split(':')[0]] = entry[:-1].split(':')[1]
				entry = stable.readline()
				c += 1
	else:
		print("Sort table not found and --no-sort wasnt specified, aborting sorting")
		sys.exit()

	make_sort_dest(sort_dest,table)
	
	for file in to_sort:
		mime = magic.from_file(file, mime=True)
		moved = False
		for mt in table.keys():
			if mime == mt:
				move_file(file,sort_dest+table[mime])
				moved = True
		if not moved:
			move_file(file,sort_dest+table['*'])

#Function to make the various directories
def make_sort_dest(sort_dir,table):
	if not os.path.isdir(sort_dir):
		os.mkdir(sort_dir)
	for key in table.keys():
		if not os.path.isdir(sort_dir+table[key]):
			os.makedirs(sort_dir+table[key], exist_ok=True)



#Configure argparser
parser = argparse.ArgumentParser()
parser.add_argument('target')
parser.add_argument('-d','--destination')
parser.add_argument('-H','--hashes')
parser.add_argument('-s','--sort-loc')
parser.add_argument('-S','--sort-dest')
parser.add_argument('-n','--no-prompt',action='store_true')
parser.add_argument('-y','--yes-prompt',action='store_true')
parser.add_argument('-o','--hash-only',action='store_true')
parser.add_argument('--no-sort',action='store_true')
args = parser.parse_args()

Target = args.target
if args.destination == None and args.hashes == None:
	print("You either need -d or -H")
	sys.exit()

if args.sort_loc == None:
	Sort_Loc = "/usr/share/FileFilter/default_sort_table"
else:
	Sort_Loc = args.sort_loc

if args.no_prompt and args.yes_prompt:
	print("Cannot specify no and yes to prompt!")
	sys.exit()
elif args.no_prompt == None and args.yes_prompt == None:
	prompt = None
elif args.no_prompt:
	prompt = False
else:
	prompt = True

#Check if hashes hasn't been defined, if it didnt, make one outside destination
if args.hashes == None:
	Destination = os.path.abspath(args.destination)
	m = re.search('^(.*/.*/).*$',Destination)
	Hashes = m.group(1)+".hashes"
	make_hashfile(Hashes,Destination,True if prompt == None else False,prompt if not prompt == None else True)
elif args.hash_only:
	Hashes = os.path.abspath(args.hashes)
	m = re.search('^(.*/.*/).*$',Target)
	make_hashfile(Hashes,Target,False)
elif not args.destination == None:
	Destination = os.path.abspath(args.destination)
	Hashes = os.path.abspath(args.hashes)
	make_hashfile(Hashes,Destination,True if prompt == None else False,prompt if not prompt == None else True)
else:
	Hashes = os.path.abspath(args.hashes)
	Destination = os.path.abspath('.')

#Sets Sort_Dest (Needed after Destination is defined) to -S or outside destination
if args.sort_dest == None and not args.hash_only:
	Sort_Dest = os.path.abspath(Destination)
	if not Sort_Dest == os.path.abspath('.'):
		m = re.search('^(.*/.*/).*$',Destination)
		Sort_Dest = m.group(1)+"Sorted/"
	else:
		Sort_Dest = Sort_Dest+"/Sorted/"
	print(Sort_Dest)
elif args.sort_dest == None:
	pass
else:
	Sort_Dest = args.sort_dest
	print(Sort_Dest)


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
if not args.hash_only:
	to_sort = []
	print("Removing Matching files...")
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
	print("Done")

#Sort using Sort_Loc to Sort_Dest is --no-sort isn't specified
if (not args.no_sort) and (not args.hash_only):
	print("Sorting File on mime type and sort table")
	sort_files(to_sort,Sort_Loc,Sort_Dest)
print("DONE!!")
