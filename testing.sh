#!/bin/sh
CLI_RED='\033[0;31m'
CLI_GREEN='\033[0;32m'
CLI_RC='\033[0m'

parse_tilde() {
	echo $1 | sed 's,~,'$HOME',g'
}

make_test_data() {
	clean_test_data
	[ ! "$1" == "-q" ] && echo -n "Making testing data..."
	if [ ! -d "./Test Target" ] && [ ! -d "./Test Destination" ]; then 
		mkdir ./Test\ Target ./Test\ Destination 
	fi
	for v in 1 2 3 4 5; do
		head -c 5M /dev/urandom > ./Test\ Destination/TEST_FILE_$v
	done
	cp ./Test\ Destination/TEST_FILE_1 ./Test\ Target/
	for v in 6 7 8 9; do
		head -c 5M /dev/urandom > ./Test\ Target/TEST_FILE_$v
	done
	[ ! "$1" == "-q" ] && echo "DONE!"
}

clean_test_data(){
rm -rf ./Test\ Target 2> /dev/null
rm -rf ./Test\ Destination 2> /dev/null
rm -rf ./.hashes 2> /dev/null
rm -rf ./Sorted 2> /dev/null
rm -rf ./test_hash_list 2> /dev/null
}

make_hash_file() {
	if [ "$1" == "" ] || [ "$1" == "-" ];then
		clean_hash_file
		make_test_data -q
		[ ! "$2" == "-q" ] && echo -n Generating hashfile and removing Target Destination...
		./FileFilter.py "./Test Destination" -H "./test_hash_list" -o 2>&1 >/dev/null
		rm -rf "./Test Destination" 2>&1 >/dev/null
		[ ! "$2" == "-q" ] && echo DONE!
	else
		clean_hash_file "$1"
		make_test_data -q
		[ ! "$2" == "-q" ] && echo -n Generating hashfile and removing Target Destination...
		./FileFilter.py "./Test Destination" -H "$(parse_tilde "$1")" -o 2>&1 >/dev/null
		rm -rf "./Test Destination" 2>&1 >/dev/null
		[ ! "$2" == "-q" ] && echo DONE!
	fi
	
}

clean_hash_file() {
	if [ "$1" == "" ] || [ "$1" == "-" ];then
		rm -rf './.hashes'
	else
		rm -rf "$1"
	fi
}

check_sorted() {
	all_files_present="true"
	for v in 6 7 8 9; do
		found="false"
		while read -r a; do
			[ ! "$(echo $a | grep TEST_FILE_$v)" == "" ] && found="true"
		done <<< $(find ./Sorted -type f)
		[ "$found" == "false" ] && all_files_present="false"
	done
	echo $all_files_present
}

check_hashfile(){
	hashfile_found="false"
	if [ -f "./.hashes" ];then
		hashfile_found="true"
	fi
	if [ "$hashfile_found" == "true" ];then
		ha=`cat ./.hashes | wc -l`
	else 
		ha=0
	fi
	if [ "$hashfile_found" == "true" ] && [ "$ha" == "5" ];then
		echo true
	else
		echo false
	fi
}

check_hashfile_custom(){
	if [ "$1" == "" ];then
		echo `check_hashfile`
	else
		hashfile_found="false"
		if [ -f "$1" ];then
			hashfile_found="true"
		fi
		if [ "$hashfile_found" == "true" ];then
			ha=`cat "$1" | wc -l`
		else 
			ha=0
		fi
		if [ "$hashfile_found" == "true" ] && [ "$ha" == "5" ];then
			echo true
		else
			echo false
		fi
	fi
}

check_testfile() {
	found_offending_file="false"
	while read -r a; do
		[ ! "$(echo $a | grep TEST_FILE_1)" == "" ] && found_offending_file="true"
	done <<< $(find ./Sorted -type f)
	while read -r a; do
		[ ! "$(echo $a | grep TEST_FILE_1)" == "" ] && found_offending_file="true"
	done <<< $(find ./Test\ Target -type f)
	[ "$found_offending_file" == "true" ] && echo false || echo true
}

check_unsorted_target(){
	all_files_present="true"
	for v in 6 7 8 9; do
		found="false"
		while read -r a; do
			[ ! "$(echo $a | grep TEST_FILE_$v)" == "" ] && found="true"
		done <<< $(find ./Test\ Target -type f)
		[ "$found" == "false" ] && all_files_present="false"
	done
	echo $all_files_present
}

test_basic() {
	make_test_data -q
	[ "$1" == "true" ] && echo "Testing ./FileFilter.py \"./Test Target\" -d \"./Test Destination\" " || echo -n "Testing ./FileFilter.py \"./Test Target\" -d \"./Test Destination\"..."
	[ "$1" == "true" ] && echo "######OUTPUT#######"
	[ "$1" == "true" ] && ./FileFilter.py "./Test Target" -d "./Test Destination" ||  ./FileFilter.py "./Test Target" -d "./Test Destination" 2>&1 >/dev/null
	[ "$1" == "true" ] && echo "###################"
	#Should be a ./Sorted folder with TEST_FILE_6 through 9
	t1="$(check_sorted)"
	#echo $t1
	#Should be a ./.hashes file with 5 hashes
	t2="$(check_hashfile)"
	#echo $t2
	#./Test Target or ./Sorted SHOULD NOT HAVE TEST_FILE_1
	t3="$(check_testfile)"
	#echo $t3
	if [ "$1" == "true" ];then
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && [ "$t3" == "true" ] && echo -e "Testing ./FileFilter.py \"./Test Target\" -d \"./Test Destination\""$CLI_GREEN" PASSED"$CLI_RC || echo -e "Testing ./FileFilter.py \"./Test Target\" -d \"./Test Destination\""$CLI_RED" FAILED"$CLI_RC 
	else
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && [ "$t3" == "true" ] && echo -e $CLI_GREEN"PASSED"$CLI_RC || echo -e $CLI_RED"FAILED"$CLI_RC 
	fi
}

test_hashfile_basic() {
	make_hash_file "-" -q
	[ "$1" == "true" ] && echo "Testing ./FileFilter.py \"./Test Target\" -H ./test_hash_list " || echo -n "Testing ./FileFilter.py \"./Test Target\" -H ./test_hash_list..."
	[ "$1" == "true" ] && echo "######OUTPUT#######"
	[ "$1" == "true" ] && ./FileFilter.py "./Test Target" -H ./test_hash_list ||  ./FileFilter.py "./Test Target" -H ./test_hash_list 2>&1 >/dev/null
	[ "$1" == "true" ] && echo "###################"
	t1="$(check_sorted)"
	t2="$(check_hashfile_custom "test_hash_list")"
	t3="$(check_testfile)"
	if [ "$1" == "true" ];then
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && [ "$t3" == "true" ] && echo -e "Testing ./FileFilter.py \"./Test Target\" -H ./test_hash_list"$CLI_GREEN" PASSED"$CLI_RC || echo -e "Testing ./FileFilter.py \"./Test Target\" -H ./test_hash_list"$CLI_RED" FAILED"$CLI_RC 
	else
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && [ "$t3" == "true" ] && echo -e $CLI_GREEN"PASSED"$CLI_RC || echo -e $CLI_RED"FAILED"$CLI_RC 
	fi
}

#Tesh with a hashfile location somwhere else (in this case HOME or ~)
test_hashfile_hashlocabs(){
	make_hash_file "~/test_hash_abs_list" -q
	[ "$1" == "true" ] && echo "Testing ./FileFilter.py \"./Test Target\" -H ~/test_hash_abs_list " || echo -n "Testing ./FileFilter.py \"./Test Target\" -H ~/test_hash_abs_list..."
	[ "$1" == "true" ] && echo "######OUTPUT#######"
	[ "$1" == "true" ] && ./FileFilter.py "./Test Target" -H ~/test_hash_abs_list ||  ./FileFilter.py "./Test Target" -H ~/test_hash_abs_list 2>&1 >/dev/null
	[ "$1" == "true" ] && echo "###################"
	t1="$(check_sorted)"
	t2="$(check_hashfile_custom "$HOME/test_hash_abs_list")"
	t3="$(check_testfile)"
	if [ "$1" == "true" ];then
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && [ "$t3" == "true" ] && echo -e "Testing ./FileFilter.py \"./Test Target\" -H ~/test_hash_abs_list"$CLI_GREEN" PASSED"$CLI_RC || echo -e "Testing ./FileFilter.py \"./Test Target\" -H ~/test_hash_abs_list"$CLI_RED" FAILED"$CLI_RC 
	else
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && [ "$t3" == "true" ] && echo -e $CLI_GREEN"PASSED"$CLI_RC || echo -e $CLI_RED"FAILED"$CLI_RC 
	fi
}

test_nosort_basic() {
	make_test_data -q
	[ "$1" == "true" ] && echo "Testing ./FileFilter.py --no-sort \"./Test Target\" -d \"./Test Destination\"" || echo -n "Testing ./FileFilter.py --no-sort \"./Test Target\" -d \"./Test Destination\"..."
	[ "$1" == "true" ] && echo "######OUTPUT#######"
	[ "$1" == "true" ] && ./FileFilter.py --no-sort "./Test Target" -d "./Test Destination" || ./FileFilter.py --no-sort "./Test Target" -d "./Test Destination" 2>&1 >/dev/null
	[ "$1" == "true" ] && echo "###################"
	t1=`check_hashfile`
	t2=`check_unsorted_target`
	if [ "$1" == "true" ];then
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && echo -e "Testing ./FileFilter.py --no-sort \"./Test Target\" -d \"./Test Destination\""$CLI_GREEN" PASSED"$CLI_RC || echo -e "Testing ./FileFilter.py --no-sort \"./Test Target\" -d \"./Test Destination\""$CLI_RED" FAILED"$CLI_RC 
	else
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && echo -e $CLI_GREEN"PASSED"$CLI_RC || echo -e $CLI_RED"FAILED"$CLI_RC 
	fi
	
}

test_nosort_hash() {
	make_hash_file "-" -q
	[ "$1" == "true" ] && echo "Testing ./FileFilter.py --no-sort \"./Test Target\" -H \"./test_hash_list\"" || echo -n "Testing ./FileFilter.py --no-sort \"./Test Target\" -H \"./test_hash_list\"..."
	[ "$1" == "true" ] && echo "######OUTPUT#######"
	[ "$1" == "true" ] && ./FileFilter.py --no-sort "./Test Target" -H "./test_hash_list" || ./FileFilter.py --no-sort "./Test Target" -H "./test_hash_list" 2>&1 >/dev/null
	[ "$1" == "true" ] && echo "###################"
	t1=`check_hashfile_custom "test_hash_list"`
	t2=`check_unsorted_target`
	if [ "$1" == "true" ];then
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && echo -e "Testing ./FileFilter.py --no-sort \"./Test Target\" -H \"./test_hash_list\""$CLI_GREEN" PASSED"$CLI_RC || echo -e "Testing ./FileFilter.py --no-sort \"./Test Target\" -H \"./test_hash_list\""$CLI_RED" FAILED"$CLI_RC 
	else
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && echo -e $CLI_GREEN"PASSED"$CLI_RC || echo -e $CLI_RED"FAILED"$CLI_RC 
	fi
	
}

test_nosort_named_hash() {
	make_hash_file "./Test Hash" -q
	[ "$1" == "true" ] && echo "Testing ./FileFilter.py --no-sort \"./Test Target\" -H \"./Test Hash\"" || echo -n "Testing ./FileFilter.py --no-sort \"./Test Target\" -H \"./Test Hash\"..."
	[ "$1" == "true" ] && echo "######OUTPUT#######"
	[ "$1" == "true" ] && ./FileFilter.py --no-sort "./Test Target" -H "./Test Hash" || ./FileFilter.py --no-sort "./Test Target" -H "./Test Hash" 2>&1 >/dev/null
	[ "$1" == "true" ] && echo "###################"
	t1=`check_hashfile_custom "Test Hash"`
	t2=`check_unsorted_target`
	if [ "$1" == "true" ];then
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && echo -e "Testing ./FileFilter.py --no-sort \"./Test Target\" -H \"./Test Hash\""$CLI_GREEN" PASSED"$CLI_RC || echo -e "Testing ./FileFilter.py --no-sort \"./Test Target\" -H \"./Test Hash\""$CLI_RED" FAILED"$CLI_RC 
	else
		[ "$t1" == "true" ] && [ "$t2" == "true" ] && echo -e $CLI_GREEN"PASSED"$CLI_RC || echo -e $CLI_RED"FAILED"$CLI_RC 
	fi
	
}

test_basic $1
test_hashfile_basic $1
test_hashfile_hashlocabs $1
test_nosort_basic $1
test_nosort_hash $1
test_nosort_named_hash $1
