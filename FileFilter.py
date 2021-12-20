#!/bin/python
import re
import hashlib
import os
import sys
import argparse
import magic

class ff:
	def md5_from_file(self,bs=2**20,nl=True):
		h = hashlib.md5()
		while True:
			data = self.file_read.read(bs)
			if not data:
				break
			h.update(data)
		return h.hexdigest() + ( "\n" if nl else "" )
	
	def make_hashfile(self):
		if os.path.isfile(self.hashes):
			if(self.prompt):
				self.prompt_answer = False if input(self.hashes+" Already exists. Do you want to use it instead of overwriting it (Y/n)?") == "n" else self.prompt
			if self.prompt_answer: #Overwritting, same as writting
				print("Making hashfile for "+self.destination)
				self.hash_file = open(self.hashes,'w')
				
				for sd,d,F in os.walk(self.destination):
					for filename in F:
						filepath = sd + os.sep + filename
						self.file_read = open(filepath,mode='rb')
						h = self.md5_from_file()
						self.file_read.close()
						self.hash_file.write(h)
				self.hash_file.close()
		else:
			self.hash_file = open(self.hashes,'w')
			#Open all files in Destination (Files to compare targets against)
			for sd,d,F in os.walk(self.destination):
				#For each file, make a hash of it and write it in the hash list
				for filename in F:
					filepath = sd + os.sep + filename
					self.file_read = open(filepath,mode='rb')
					h = self.md5_from_file()
					self.file_read.close()
					self.hash_file.write(h)
			self.hash_file.close()
	
	def __init__(self,target,destination,hashes,sort_loc,sort_dest,no_prompt,yes_prompt,no_sort,hash_only):
		self.hashes = hashes
		self.target = target
		self.destination = destination 
		self.sort_loc = sort_loc
		self.sort_dest = sort_dest
		self.no_prompt = no_prompt
		self.yes_prompt = yes_prompt
		self.no_sort = no_sort
		self.hash_only = hash_only
		if self.destination == None and self.hashes == None:
			print("You either need -d or -H")
			sys.exit()
		
		if args.sort_loc == None:
			self.sort_loc = "/usr/share/FileFilter/default_sort_table"
		
		if self.no_prompt and self.yes_prompt:
			print("Cannot specify no and yes to prompt!")
			sys.exit()
		elif self.no_prompt == None and self.yes_prompt == None:
			self.prompt = None
		elif args.no_prompt:
			self.prompt = False
		else:
			self.prompt = True
		self.prompt_answer = True if self.prompt == None else False
		self.prompt = self.prompt if not self.prompt == None else True
		
		if self.hashes == None:
			self.destination = os.path.abspath(self.destination)
			m = re.search('^(.*/.*/).*$',self.destination)
			self.hashes = m.group(1)+".hashes"
			self.make_hashfile()
		elif args.hash_only:
			self.hashes = os.path.abspath(self.hashes)
			self.destination = self.target
			m = re.search('^(.*/.*/).*$',self.target)
			self.make_hashfile()
		elif not args.destination == None:
			self.destination = os.path.abspath(args.destination)
			self.hashes = os.path.abspath(args.hashes)
			self.make_hashfile()
		else:
			self.hashes = os.path.abspath(self.hashes)
			self.destination = os.path.abspath('.')
		
		if self.sort_dest == None and not self.hash_only:
			self.sort_dest = os.path.abspath(self.destination)
			if not self.sort_dest == os.path.abspath('.'):
				m = re.search('^(.*/.*/).*$',self.destination)
				self.sort_dest = m.group(1)+"Sorted/"
			else:
				self.sort_dest = self.sort_dest+"/Sorted/"
			print(self.sort_dest)
	
	def read_hashes(self):
		self.hash_list = []
		with open(self.hashes,'r') as hashes:
			h4sh = hashes.readline()
			while h4sh:
				self.hash_list.append(h4sh[:-1])
				h4sh = hashes.readline()
	
	def filter(self):
		if not self.hash_only:
			self.to_sort = []
			print("Removing Matching files...")
			for sd,d,F in os.walk(self.target):
				for filename in F:
					filepath = sd + os.sep + filename
					self.file_read = open(filepath,mode='rb')
					h = self.md5_from_file(nl=False)
					found = False
					for comp in self.hash_list:
						#If theres a match, remove that file
						if h == comp:
							os.remove(filepath)
							found = True
							break
					
					if not found:
						#Otherwise, get Add to the to_sort array
						self.to_sort.append(filepath)
					self.file_read.close()
			print("Done")
	
	def make_sort_dest(self):
		if not os.path.isdir(self.sort_dest):
			os.mkdir(self.sort_dest)
		for key in self.table.keys():
			if not os.path.isdir(self.sort_dest+self.table[key]):
				os.makedirs(self.sort_dest+self.table[key], exist_ok=True)
	
	def move_file(self,file,dest):
		os.rename(file,dest+os.path.basename(file))
		return dest+os.path.basename(file)
	
	def sort(self):
		if (not self.no_sort) and (not self.hash_only):
			print("Sorting File on mime type and sort table")
			if os.path.isfile(self.sort_loc):
				self.table = {}
				with open(self.sort_loc,'r') as stable:
					entry = stable.readline()
					while entry:
						if not ( entry[:-1] == "" or entry[0] == "#"):
							self.table[entry[:-1].split(':')[0]] = entry[:-1].split(':')[1]
						entry = stable.readline()
			else:
				print("Sort table not found and --no-sort wasnt specified, aborting sorting")
				sys.exit()
	
			self.make_sort_dest()
			
			for file in self.to_sort:
				mime = magic.from_file(file, mime=True)
				moved = False
				for mt in self.table.keys():
					if mime == mt:
						self.move_file(file,self.sort_dest+self.table[mime])
						moved = True
				if not moved:
					self.move_file(file,self.sort_dest+self.table['*'])

#Configure argparser
if __name__ == "__main__":
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
	
	filefilter = ff(args.target,args.destination,args.hashes,args.sort_loc,args.sort_dest,args.no_prompt,args.yes_prompt,args.no_sort,args.hash_only)
	
	#Open hashes in read mode, get all hashes from files, removes trailing newline and stores them in a list
	filefilter.read_hashes()
	
	#Open all file in Target
	#For each file, make a hash of it and compare it against the hash list
	filefilter.filter()
	
	#Sort using Sort_Loc to Sort_Dest is --no-sort isn't specified
	filefilter.sort()
	print("DONE!!")
