# FileFilter
**Takes Files from folder A and remove duplicates against** either **a list of hashes or** hashes made **from folder B. Then it sorts the files** based on mime type **to folder C** 
## Installing

> Requires Python3, Python3 Pip
1. cd to repo folder
1. 
    `git clone https://github.com/case-prudolicce/FileFilter.git`
1. 
    `cd FileFilter`
1. 
    `make install` (with proper priviliges)
## Basic Usage:

```bash 
#Most basic, creates the hash list and the sorting destination called SORTED outside destination and filters,sorts.
ff <TARGET> -d <DESTINATION>
#Or if you want to use a premade hash list
ff <TARGET> -H <HASH LIST LOCATION>
#Or if you want to specify the name and location of the hash list when its made
ff <TARGET> -d <DESTINATION> -H <HASH LIST NAME/LOCATION>
```

## Arguments

> **You need** `TARGET` **and either** `-d DESTINATION` **or** `-H HASHES` (**if** `-o` isn't specified)
* `TARGET` : The folder you want to filter down (Mandatory, will remove duplicates and sort them)
* `-d <DESTINATION>` : Destination folder (Will make a hash list out of it) 
> If `-d` is not paired with `-H`, it will make the hash list outside `DESTINATION` and name it `.hashes`
* `-h` : Display Help
* `-H <HASHES>` : **Used alone**, the hash list location to use (instead of making one from `DESTINATION`). **With -d However**, this now indicates what name the generated hash list should be using
* `--no-sort`: Do not sort the filtered file, do not use sort list. only remove duplicates and make a hashlist
* `-s <SORT_LOC>` : Location of the sort table (file dictating where which mime type should be sorted where). See more below
* `-S <SORT_DEST>` : Destination for sorted file to go to (from whom `SORT_LOC` is based from).
> By Default is `-S` isnt specified the sorting location will be outside destination, in a folder named `SORTED`
* `-n` (`--no-prompt`) / `-y` (`--yes-prompt`) : When prompting to overwrite a hashfile, yes or no (removes prompt)
* `-o` / `--hash-only` : when this option is passed, FileFilter will only make a hash list from `TARGET`

## The Sort Table

The Sort table is a file that tells FileFilter where each mime type matched should go.

Heres an example of what the default sort table looks like:
```bash
text/plain:/TEXT/
text/x-shellscript:/CODING/SCRIPT/POSIX
#etc...
*:/NOT FOUND/
```
Each line is separated in 2 parts: The mime type and the location

* #### [The mime type is a marker for any given file](https://stackoverflow.com/questions/3828352/what-is-a-mime-type "Mime Type")

* #### The Location is the path (from `SORT_DEST`) that the given mime type binds to

> `*:<PATH>` **Is required** and should be the default path from `SORT_DEST` if no mime type was matched.

If no sort_table is provided (`-s`) the default one will be used, located at `/usr/`

## Uninstalling

1. 
    cd to repo folder
1. 
    `cd FileFilter`
1. 
    `make uninstall`
