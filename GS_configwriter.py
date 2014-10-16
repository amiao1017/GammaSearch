#!/usr/bin/python

# python clone of ConfigFileWriter_v4.pl

# input: source number, location of configtable of source parameters from 2FGL catalog
# output: config files for use in gammasearch investigation

import sys, os
import getopt
import numpy as np

def main(argv):

	catalogFile = ''
	sourceNumber = ''
	outputDir = '.'

	Tau = 300
	Mismatch = 0.2
	startTime = 970840605
	TObs = 432000
	TwoF = 40

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

	# check that outputDir exists, make if it does not

	if not(os.path.isdir(outputDir)):
		os.makedirs(outputDir)

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
		f.write("#Configuration File for GammaSearch\n")
		f.write("[InjVars]\n")
		f.write("#H1 Input Data\n")
		f.write("H1InputData=/home/jaclyn.sanders/SFTs/H1/*.sft\n")
		f.write("#L1 Input Data\n")
		f.write("L1InputData=/home/jaclyn.sanders/SFTs/L1/*.sft\n")
		f.write("#Source Number\n")
 		f.write("Source="+str(sourceNumber)+"\n")
		f.write("#Alpha (rad)\n")
		f.write("Alpha="+str(Alpha)+"\n")
		f.write("#Delta (rad)\n")
		f.write("Delta="+str(Delta)+"\n")
		f.write("#Semimajor (rad)\n")
		f.write("Semimajor="+str(Semimajor)+"\n")
		f.write("#Semiminor (rad)\n")
		f.write("Semiminor="+str(Semiminor)+"\n")
		f.write("#Semiangle (rad)\n")
		f.write("Semiangle="+str(Semiangle)+"\n")
		f.write("#Assumed Age (Years)\n")
		f.write("Age=" + str(Tau) + "\n")
		f.write("#Mismatch\n")
		f.write("Mismatch=" + str(Mismatch) + "\n")
		f.write("#Start Time\n")
		f.write("StartTime=" + str(startTime) + "\n")
		f.write("#Threshold for 2F\n")
		f.write("2F=" + str(TwoF) + "\n")
		f.write("# Ephemeris path for MFD\n")
		f.write("EphemPath=/home/sano/master/opt/lscsoft/lalpulsar/share/lalpulsar\n")
		f.write("# Ephemeris years for MFD\n")
		f.write("EphemYears=09-11\n")
		f.write("# Ephemeris earth for CFS\n")
		f.write("EphemEarth=/mnt/qfs2/jaclyn.sanders/earth00-19-DE405.dat.gz\n")
		f.write("# Ephemeris sun for CFS\n")
		f.write("EphemSun=/mnt/qfs2/jaclyn.sanders/sun00-19-DE405.dat.gz\n")
	

if __name__ == "__main__":
	main(sys.argv[1:])




