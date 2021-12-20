#!/bin/python
import unittest
import shutil
import os

class TestFF(unittest.TestCase):
	def parse_home(self,p):
		return p.replace("~",os.path.expanduser("~"))
	
	#Makes ./Test Target/Destination
	#Makes 5 ./Test Destination/TEST_FILE_X 
	#Copy ./Test Destination/TEST_FILE_1 to ./Test Target/TEST_FILE_1 (Duplicate test file)
	#Create 4 more TEST_FILE_X files in ./Test Target/
	#
	#End result should be 2 folder (Test Target/Destination) with 5 files each.
	#TEST_FILE_1 should be the same file in both dirs
	def make_test_data(self):
		if not os.path.exists("./Test Target"):
			os.mkdir("./Test Target")
		if not os.path.exists("./Test Destination"):
			os.mkdir("./Test Destination")
		for i in range(1,6):
			f = open("./Test Destination/TEST_FILE_"+str(i),"wb")
			f.write(os.urandom(50))
			f.close()
		shutil.copy("./Test Destination/TEST_FILE_1","./Test Target/TEST_FILE_1")
		for i in range(6,10):
			f = open("./Test Target/TEST_FILE_"+str(i),"wb")
			f.write(os.urandom(50))
			f.close()
	
	#Should make the same data as make_test_data, with ./Test Destination/ replaced with a hash list called "test_hash_list"
	def make_hashfile_test_data(self,hn = "./test_hash_list"):
		self.clean_test_data()
		self.make_test_data()
		os.system("./FileFilter.py \"./Test Destination\" -H \""+self.parse_home(hn)+"\" -o >/dev/null")
		shutil.rmtree("./Test Destination")

	#Removes ./.hashes, ./Test Target|Destination, ./Sorted and ./test_hash_list (if found)
	def clean_test_data(self,hn = "./.hashes"):
		if os.path.exists("./Test Target"):
			shutil.rmtree("./Test Target")
		if os.path.exists("./Test Destination"):
			shutil.rmtree("./Test Destination")
		if os.path.exists(hn):
			os.remove(hn)
		if os.path.exists("./.hashes"):
			os.remove("./.hashes")
		if os.path.exists("./Sorted"):
			shutil.rmtree("./Sorted")
		if os.path.exists("./test_hash_list"):
			os.remove("./test_hash_list")

	#Verifies that ./Sorted exists
	#Verifies that ./Sorted has 4 file TEST_FILE_{6,7,8,9}
	def check_sorted(self) -> bool:
		if os.path.exists("./Sorted"):
			ret = True
			for i in range(6,10):
				test_file_found = False
				for (dirpath, dirnames, filenames) in os.walk("./Sorted"):
					for f in filenames:
						if f == "TEST_FILE_"+str(i):
							test_file_found = True
				if not test_file_found:
					return False
			return ret
		else:
			return False
	
	#Verifies that `hn` exists
	#Verifies that `hn` has 5 hashes (from ./Test Destination/TEST_FILE_{1,2,3,4,5}
	def check_hashfile(self, hn = "./.hashes") -> bool:
		if os.path.exists(hn):
			f = open(hn)
			num_lines = sum(1 for line in f)
			f.close()
			if num_lines == 5:
				return True
			else:
				return False
		else:
			return False

	#Verifies that TEST_FILE_1 is only present in ./Test Destination (Not in ./Sorted or ./Test Target)
	def check_testfile(self) -> bool:
		if os.path.exists("./Sorted/TEST_FILE_1") or os.path.exists("./Test Target/TEST_FILE_1") :
			return False
		else:
			return True
	
	#Counterpart to check_sorted, does the same but to ./Test Target (when --no-sort is used)
	def check_target(self) -> bool:
		if os.path.exists("./Test Target"):
			ret = True
			for i in range(6,10):
				test_file_found = False
				for (dirpath, dirnames, filenames) in os.walk("./Test Target"):
					for f in filenames:
						if f == "TEST_FILE_"+str(i):
							test_file_found = True
				if not test_file_found:
					return False
			return ret
		else:
			return False
	
	
	def test_hashfile_basic(self):
		self.clean_test_data()
		self.make_hashfile_test_data()
		os.system("./FileFilter.py \"./Test Target\" -H \"./test_hash_list\" >/dev/null")
		self.assertTrue(self.check_sorted())
		self.assertTrue(self.check_hashfile("test_hash_list")) 
		self.assertTrue(self.check_testfile())
		self.clean_test_data()
	
	def test_basic(self):
		self.clean_test_data()
		self.make_test_data()
		os.system("./FileFilter.py \"./Test Target\" -d \"./Test Destination\" >/dev/null")
		self.assertTrue(self.check_sorted())
		self.assertTrue(self.check_hashfile()) 
		self.assertTrue(self.check_testfile())
		self.clean_test_data()
	
	def test_absolute_hashfile(self):
		self.clean_test_data()
		self.make_hashfile_test_data(hn="~/test_hash_abs_list")
		os.system("./FileFilter.py \"./Test Target\" -H ~/test_hash_abs_list >/dev/null")
		self.assertTrue(self.check_sorted())
		self.assertTrue(self.check_hashfile(os.path.expanduser("~")+"/test_hash_abs_list")) 
		self.assertTrue(self.check_testfile())
		self.clean_test_data(hn=os.path.expanduser("~")+"/test_hash_abs_list")

	def test_no_sort_hash(self):
		self.clean_test_data()
		self.make_hashfile_test_data()
		os.system("./FileFilter.py --no-sort \"./Test Target\" -H \"./test_hash_list\" >/dev/null")
		self.assertTrue(self.check_target())
		self.assertTrue(self.check_hashfile("test_hash_list")) 
		self.assertTrue(self.check_testfile())
		self.clean_test_data()

	def test_no_sort_basic(self):
		self.clean_test_data()
		self.make_test_data()
		os.system("./FileFilter.py --no-sort \"./Test Target\" -d \"./Test Destination\" >/dev/null")
		self.assertTrue(self.check_target())
		self.assertTrue(self.check_hashfile()) 
		self.assertTrue(self.check_testfile())
		self.clean_test_data()

	def test_no_sort_named_hashfile(self):
		self.clean_test_data()
		self.make_hashfile_test_data(hn="Test Hash File")
		os.system("./FileFilter.py --no-sort \"./Test Target\" -H \"./Test Hash File\" >/dev/null")
		self.assertTrue(self.check_target())
		self.assertTrue(self.check_hashfile("Test Hash File")) 
		self.assertTrue(self.check_testfile())
		self.clean_test_data(hn="./Test Hash File")

if __name__ == "__main__":
	tff = TestFF()
	tff.test_basic()
