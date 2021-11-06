# Features to add
* Fancy display when generating hash file and filtering (removing duplicates and sorting)
* Exclusion list (-e)
    * Exclusion Rules
* Sort only option (Do not use hash file, do not remove duplicates) (--sort-only)
* Verbose option (-v)
* Man Page
* Windows compatible version
* OOP Transition
* -m option (max bytes for hash)
* Better test units
# Bugs to fix
* If the sort table, destination or the hash list is in the target folder, it will get removed
* Doesnt remove duplicate within its own directory
* Random None pops up
* The sorted folder get made outside/in the same directory as hash when invoking like so: `./FileFilter.py "./Test Target" -H ~/test\_hash\_abs\_list` (Sorted should be at . yet it is at ~)
