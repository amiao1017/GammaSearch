#!/usr/bin/python

# GS_UL_ratios - collects results from upper limit validations and produces strain estimates.

from __future__ import division
import sys, getopt, array, ConfigParser, math
import numpy as np

def main(argv):

	usage = "GS_UL_ratios -r <record file> -s <start frequency> [-d <input directory> -o <output file>]"

	inputDir = "."
	
	try:
		opts, args = getopt.getopt(argv, "hr:s:d:o:", ["help", "recordFile=", "startFreq=","inputDir=", "outputFile="])
	except getopt.GetoptError:
		print usage
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print usage
			sys.exit()
		elif opt in ("-r", "--recordFile"):
			recordfile = arg
		elif opt in ("-s", "--startFreq"):
			startFreq = arg
		elif opt in ("-d", "--inputDir"):
			inputDir = arg
		elif opt in ("-o", "--outputFile"):
			outfile = arg

	try:
		search_record = np.loadtxt(recordfile,skiprows=1)
	except:
		sys.stderr.write("Invalid record file " + recordfile)
		sys.exit(1)
	
	try:
		outfile
	except:
		outfile = "UL_ratios_" + startFreq + ".txt"



	#index along search record.

	frequency = []
	strain = []
	found = []
	searched = []
	ratio = []

	for a in search_record:

		maxFstat = 0
		h0 = a[0]
		search = a[1]
		twoF0 = a[2]
		freq = math.floor(a[4])
		
		filename = "CFS_Out_Freq_" + str(freq) + "_Test_" + str(int(search)) + ".dat"

		location = inputDir + "/strain_" + str(h0) + "/" + filename

		with open(location, 'r') as input:
			data = input.readlines()[20:-1]


		for line in data:
			line = line.strip()
			columns = line.split()
			source = {}
			source['Fstat'] = columns[6]
			source['FstatH1'] = columns[7]
			source['FstatL1'] = columns[8]
			
			if FStatVeto(source['Fstat'], source['FstatH1'], source['FstatL1']) and (source['Fstat'] > maxFstat):
				twoF = source['Fstat']
				break 

			twoF = 0
			
		
		if (h0 not in strain) or (h0 != strain[-1]):
			frequency.append(freq)
			strain.append(h0)
			searched.append(1)
			if twoF >= twoF0:
				found.append(1)
			else:
				found.append(0)
		else:
			searched[-1] = searched[-1] + 1
			if twoF >= twoF0:
				found[-1] = found[-1] + 1

	for b in range(0, len(found)-1):
		ratio.append(found[b]/searched[b])

 	with open(outfile,'w') as f:

                f.write("Frequency Strain Found Searched Ratio\n")

                for c in range(0,len(ratio)-1):

                        f.write(str(frequency[c]) + " " + str(strain[c]) + " " + str(found[c]) + " " + str(searched[c]) + " " + str(ratio[c]) + "\n")
		 
def FStatVeto(FStat, FStatH1, FStatL1):
	
	FStat = float(FStat)
	FStatH1 = float(FStatH1)
	FStatL1 = float(FStatL1)
	
	#vetoing function: consistency check for UL searches.
	#vetos if joint is lower than max of single IFOs or if either single IFO is less than 15
	
	if (FStat > FStatH1) and (FStat > FStatL1) and (FStatL1 > 15) and (FStatH1 > 15):
		return 1
	else:
		return 0

if __name__ == "__main__":
	main(sys.argv[1:])

