patronage opendata exercise 2
=============================

This repository contains BLStream patronage challenge solution from the
OpenData track.

installation
------------

This program requires python 3.1+ and have extra dependencies:
 - pymongo

You should be able to run it from the command line after installing python
interpreter and this one extra module

configuration
-------------

configuration file contains location of Mongo database (host name and port ).
This script works better if MongoDB server is present and responding, so before
running it make sure that configuration is correct for your environment.

usage
-----

run from this command from the console:

	$> python csv2json.py --help

to get this help screen:

	usage: csv2json.py [-h] -c CONFIG {import,drop_all,list_all} ...
	
	BLStream patronage challenge solution
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -c CONFIG, --config CONFIG
							configuration file
	
	commands:
	  {import,drop_all,list_all}
							type <command> --help/-h for extra help
		import              import file to db
		drop_all            drop all objects
		list_all            list all objects



Importing from file to the database can be achieved with:

	python3 csv2json.py -c config.ini import CsvSampleOpenData\ Zadanie\ 1.csv
	
Listing of all records can be retrieved with following command:

	python3 csv2json.py -c config.ini list_all
