#!/usr/bin/python

# python clone of ConfigFileWriter_v4.pl

# input: source number, location of configtable of source parameters from 2FGL catalog
# output: config files for use in gammasearch investigation

import sys
import getopt
import numpy as np

def main(argv):

	catalogFile = ''
	sourceNumber = ''
	outputDir = '.'

	usage = "GS_configwriter -s <sourcenumber> -c <catalogfile> [-o <outputDir>]"

	#load options

	try:
		opts, args = getopt.getopt(argv, "hs:c:o:", ["help", "source=","catalog=","outputDir="])
	except getopt.GetoptError:
		print usage
		sys.exit(2)

	for opt, arg in opts:	
		if opt == ("-h"):
			print usage
			sys.exit()
		elif opt in ("-s", "--source"):
			sourceNumber = int(arg)
		elif opt in ("-c", "--catalog"):
			catalogFile = arg
		elif opt in ("-o", "--outputDir"):
			outputDir = arg

	#load catalog
	
	try:
		catalog = np.loadtxt(catalogFile, delimiter=",")
	except IOError:
		print 'Error: invalid catalog location'
		sys.exit(2)
	for source in range(0,len(catalog)-1):
		if sourceNumber == catalog[source,0]:
			catalogIndex = source

	# test if source was found in catalog.

	try:
		catalogIndex
	except NameError:
		print "Error: source index not in catalog.\n"
		sys.exit(2)
	
	Alpha = catalog[catalogIndex,1]
	Delta = catalog[catalogIndex,2]
	Semimajor = catalog[catalogIndex,3]
	Semiminor = catalog[catalogIndex,4]
	Semiangle = catalog[catalogIndex,5]

	outputFilename = "ConfigFile_" + str(sourceNumber) + ".ini"	

	with open(outputDir+"/"+outputFilename, 'w') as f:
 		f.write("Source="+str(sourceNumber)+"\n")
		f.write("Alpha="+str(Alpha)+"\n")
		f.write("Delta="+str(Delta)+"\n")
		f.write("Semimajor="+str(Semimajor)+"\n")
		f.write("Semiminor="+str(Semiminor)+"\n")
		f.write("Semiangle="+str(Semiangle)+"\n")
		f.write("H1SFTlocation=/home/jaclyn.sanders/SFTs/H1/*.sft\n")
		f.write("L1SFTlocation=/home/jaclyn.sanders/SFTs/L1/*.sft\n")


	

if __name__ == "__main__":
	main(sys.argv[1:])




