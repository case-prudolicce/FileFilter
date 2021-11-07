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
