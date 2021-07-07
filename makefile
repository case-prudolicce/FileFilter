install:
	pip install python-magic
	if [ ! -d "/usr/share/FileFilter/" ]; then mkdir /usr/share/FileFilter/;fi
	cp ./default_sort_table /usr/share/FileFilter
	cp ./FileFilter.py /bin/ff
	chmod +x /bin/ff

uninstall:
	pip uninstall python-magic
	if [ -f "/bin/ff" ]; then rm /bin/ff;fi
	if [ -f "/usr/share/FileFilter/default_sort_table" ]; then rm /usr/share/FileFilter/default_sort_table;fi
	if [ -d "/usr/share/FileFilter/" ]; then rmdir /usr/share/FileFilter/;fi

test_data: clean_test
	@echo making test data....
	@if [ ! -d "./Test Target" ] && [ ! -d "./Test Destination" ]; then mkdir ./Test\ Target ./Test\ Destination; fi;
	@for v in 1 2 3 4 5; do \
		head -c 5M /dev/urandom > ./Test\ Destination/TEST_FILE_$$v;\
	done
	@cp ./Test\ Destination/TEST_FILE_1 ./Test\ Target/
	@for v in 6 7 8 9; do \
		head -c 5M /dev/urandom > ./Test\ Target/TEST_FILE_$$v;\
	done
	@echo done!

test_data_hash: test_data
	./FileFilter.py "./Test Destination" -H ./test_hash_list -o
	@rm -rf ./Test\ Destination

clean_test:
	@rm -rf ./Test*
	@rm -rf ./test*
	@rm -f ./.hashes
	@rm -rf ./Sorted/

test: test_data
	@echo "#######################################"
	@echo "Basic test Using A destination folder"
	@echo "#######################################"
	@echo "Target folder to filter: ./Test Target"
	@tree ./Test\ Target
	@echo "Target folder to compare target against: ./Test Destination"
	@tree ./Test\ Destination
	@echo
	./FileFilter.py "./Test Target" -d "./Test Destination"
	@echo
	@echo "Target folder filered: ./Sorted"
	@tree ./Sorted
	@echo "Target folder to that was used: ./Test Destination"
	@tree ./Test\ Destination

hash_test: test_data_hash
	@echo "#######################################"
	@echo "Basic test Using A hash list"
	@echo "#######################################"
	@echo "Target folder to filter: ./Test Target"
	@tree ./Test\ Target
	@echo "Target hash list to use: ./test_hash_list"
	@file ./test_hash_list
	@echo
	./FileFilter.py "./Test Target" -H ./test_hash_list
	@echo
	@echo "Target folder filered: ./Sorted"
	@tree ./Sorted
	@echo "Target hash list that was used: ./test_hash_list"
	@file ./test_hash_list

hash_name_test: test_data_hash
	@echo "#######################################"
	@echo "Basic test using a named hash list"
	@echo "#######################################"
	@echo "Target folder to filter: ./Test Target"
	@tree ./Test\ Target
	@echo "Target hash list to make: ./Test Hash"
	@echo
	./FileFilter.py "./Test Target" -d "./Test Destination" -H "./Test Hash"
	@echo
	@echo "Target folder filered: ./Sorted"
	@tree ./Sorted
	@echo "Target hash list that was used: ./Test Hash"
	@file ./Test\ Hash


nosort_test: test_data
	@echo "#######################################"
	@echo "No sorting test using A destination folder"
	@echo "#######################################"
	@echo "Target folder to filter: ./Test Target"
	@tree ./Test\ Target
	@echo "Target folder to compare target against: ./Test Destination"
	@tree ./Test\ Destination
	@echo
	./FileFilter.py --no-sort "./Test Target" -d "./Test Destination"
	@echo
	@echo "Target folder filered: ./Test Target"
	@tree ./Test\ Target
	@echo "Target folder to that was used: ./Test Destination"
	@tree  ./Test\ Destination

hash_nosort_test: test_data_hash
	@echo "#######################################"
	@echo "No sorting test using a hash list"
	@echo "#######################################"
	@echo "Target folder to filter: ./Test Target"
	@tree ./Test\ Target
	@echo "Target hash list to use: ./test_hash_list"
	@file ./test_hash_list
	@echo
	./FileFilter.py --no-sort "./Test Target" -H "./test_hash_list"
	@echo
	@echo "Target folder filered: ./Test Target"
	@tree ./Test\ Target
	@echo "Target hash list that was used: ./test_hash_list"
	@file ./test_hash_list

hash_name_nosort_test: test_data_hash
	@echo "#######################################"
	@echo "No sorting test using a named hash list"
	@echo "#######################################"
	@echo "Target folder to filter: ./Test Target"
	@tree ./Test\ Target
	@echo "Target hash list to use: ./test_hash_list"
	@file ./test_hash_list
	@echo
	./FileFilter.py "./Test Target" -d "./Test Destination" -H "./Test Hash" --no-sort
	@echo
	@echo "Target folder filered: ./Test Target"
	@tree ./Test\ Target
	@echo "Target hash list that was used: ./Test Hash"
	@file ./Test\ Hash

all_test:
	@$(MAKE) --no-print-directory test
	@$(MAKE) --no-print-directory hash_test
	@$(MAKE) --no-print-directory hash_name_test
	@$(MAKE) --no-print-directory nosort_test
	@$(MAKE) --no-print-directory hash_name_nosort_test