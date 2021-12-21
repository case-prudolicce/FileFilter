#!/bin/python
import unittest
import shutil
import os

class TestFF(unittest.TestCase):
	#HELPER FUNCTIONS
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
		os.system("ff \"./Test Destination\" -H \""+self.parse_home(hn)+"\" -o >/dev/null")
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
	
	#CHECK FUNCTIONS
	
	#Verifies that ./Sorted exists
	#Verifies that ./Sorted has 4 file TEST_FILE_{6,7,8,9}
	def check_sorted(self):
		self.assertTrue(os.path.exists("./Sorted"))
		missing_files = False
		for i in range(6,10):
			test_file_found = False
			for (dirpath, dirnames, filenames) in os.walk("./Sorted"):
				for f in filenames:
					if f == "TEST_FILE_"+str(i):
						test_file_found = True
			if not test_file_found:
				missing_files = True
		self.assertFalse(missing_files)

	def check_no_sorted(self):
		self.assertFalse(os.path.exists("./Sorted"))
	
	#Verifies that `hn` exists
	#Verifies that `hn` has 5 hashes (from ./Test Destination/TEST_FILE_{1,2,3,4,5}
	def check_hashfile(self, hn = "./.hashes"):
		self.assertTrue(os.path.exists(hn))
		f = open(hn)
		self.assertEqual(sum(1 for line in f),5)
		f.close()

	#Verifies that TEST_FILE_1 is only present in ./Test Destination (Not in ./Sorted or ./Test Target)
	def check_testfile(self):
		self.assertFalse(os.path.exists("./Sorted/TEST_FILE_1") or os.path.exists("./Test Target/TEST_FILE_1"))
	
	#Counterpart to check_sorted, does the same but to ./Test Target (when --no-sort is used)
	def check_target(self):
		self.assertTrue(os.path.exists("./Test Target"))
		missing_files = False
		for i in range(6,10):
			test_file_found = False
			for (dirpath, dirnames, filenames) in os.walk("./Test Target"):
				for f in filenames:
					if f == "TEST_FILE_"+str(i):
						test_file_found = True
			if not test_file_found:
				missing_files = True
		self.assertFalse(missing_files)

	def check_sorted_target(self):
		self.assertTrue(os.path.exists("./Test Target"))
		self.assertEqual(len(os.listdir("./Test Target")),0)

	def check_full_destination(self):
		self.assertTrue(os.path.exists("./Test Destination"))
		self.assertTrue(os.path.exists("./Test Destination/TEST_FILE_1"))
		self.assertTrue(os.path.exists("./Test Destination/TEST_FILE_2"))
		self.assertTrue(os.path.exists("./Test Destination/TEST_FILE_3"))
		self.assertTrue(os.path.exists("./Test Destination/TEST_FILE_4"))
		self.assertTrue(os.path.exists("./Test Destination/TEST_FILE_5"))

	def check_removed_destination(self):
		self.assertFalse(os.path.exists("./Test Destination"))
	
	#TESTS
	
	#	INPUTS
	#Target: "./Test Target"
	#Hash List: "./test_hash_list"
	#	EXPECTED
	#Sorted directory: ./Sorted 
	#(untouched) 5 hash long file: ./test_hash_list
	#Empty target directory: ./Test Target
	#No file name TEST_FILE_1 in ./Test Target OR ./Sorted (and it's subdirectories)
	#No directory ./Test Destination
	def test_hashfile_basic(self):
		self.clean_test_data()
		self.make_hashfile_test_data()
		os.system("ff \"./Test Target\" -H \"./test_hash_list\" >/dev/null")
		
		self.check_sorted()
		self.check_hashfile("test_hash_list")
		self.check_sorted_target()
		self.check_testfile()
		self.check_removed_destination()
		
		self.clean_test_data()

	#	INPUTS
	#Target: "./Test Target"
	#Destination: "./Test Destination"
	#	EXPECTED
	#Sorted directory: ./Sorted
	#5 hash long file: ./.hashes
	#Empty target directory: ./Test Target
	#No file TEST_FILE_1 in ./Test Target OR ./Sorted (and it's subdirectories)
	#(untouched) Full ./Test Destination
	def test_basic(self):
		self.clean_test_data()
		self.make_test_data()
		os.system("ff \"./Test Target\" -d \"./Test Destination\" >/dev/null")

		self.check_sorted()
		self.check_hashfile()
		self.check_sorted_target()
		self.check_testfile()
		self.check_full_destination()
		
		self.clean_test_data()
	
	#	INPUTS
	#Target: "./Test Target"
	#Hash List: ~/test_hash_abs_list
	#	EXPECTED
	#Sorted directory: ./Sorted
	#5 hash long file: ~/test_hash_abs_list
	#Empty target directory: ./Test Target
	#No file TEST_FILE_1 in ./Test Target OR ./Sorted (and it's subdirectories)
	#No directory ./Test Destination
	def test_absolute_hashfile(self):
		self.clean_test_data()
		self.make_hashfile_test_data(hn="~/test_hash_abs_list")
		os.system("ff \"./Test Target\" -H ~/test_hash_abs_list >/dev/null")
		
		self.check_sorted()
		self.check_hashfile(os.path.expanduser("~")+"/test_hash_abs_list")
		self.check_sorted_target()
		self.check_testfile()
		self.check_removed_destination()
		
		self.clean_test_data(hn=os.path.expanduser("~")+"/test_hash_abs_list")

	#	INPUTS
	#Target: "./Test Target"
	#Hash List: "./test_hash_list"
	# --no-sort option
	#	EXPECTED
	#No Sorted
	#./Test Target with 4 files (Missing TEST_FILE_1)
	#5 hash long file: ./test_hash_list
	#No file TEST_FILE_1 in ./Test Target OR ./Sorted (and it's subdirectories)
	#No directory ./Test Destination
	def test_no_sort_hash(self):
		self.clean_test_data()
		self.make_hashfile_test_data()
		os.system("ff --no-sort \"./Test Target\" -H \"./test_hash_list\" >/dev/null")
		self.check_no_sorted()
		self.check_target()
		self.check_hashfile("test_hash_list")
		self.check_testfile()
		self.check_removed_destination()
		
		self.clean_test_data()

	#	INPUTS
	#Target: "./Test Target"
	#Destination: "./Test Destination"
	# --no-sort option
	#	EXPECTED
	#No Sorted
	#./Test Target with 4 files (Missing TEST_FILE_1)
	#5 hash long file: ./.hashes
	#No file TEST_FILE_1 in ./Test Target OR ./Sorted (and it's subdirectories)
	#Full ./Test Destination
	def test_no_sort_basic(self):
		self.clean_test_data()
		self.make_test_data()
		os.system("ff --no-sort \"./Test Target\" -d \"./Test Destination\" >/dev/null")
		self.check_no_sorted()
		self.check_target()
		self.check_hashfile()
		self.check_testfile()
		self.check_full_destination()
		
		self.clean_test_data()

	#	INPUTS
	#Target: "./Test Target"
	#Hash List: "./Test Hash File"
	# --no-sort option
	#	EXPECTED
	#No Sorted
	#./Test Target with 4 files (Missing TEST_FILE_1)
	#5 hash long file: ./Test Hash File
	#No file TEST_FILE_1 in ./Test Target OR ./Sorted (and it's subdirectories)
	#No directory ./Test Destination
	def test_no_sort_named_hashfile(self):
		self.clean_test_data()
		self.make_hashfile_test_data(hn="Test Hash File")
		os.system("ff --no-sort \"./Test Target\" -H \"./Test Hash File\" >/dev/null")
		self.check_no_sorted()
		self.check_target()
		self.check_hashfile("Test Hash File")
		self.check_testfile()
		self.check_removed_destination()
		
		
		self.clean_test_data(hn="./Test Hash File")

if __name__ == "__main__":
	unittest.main()
