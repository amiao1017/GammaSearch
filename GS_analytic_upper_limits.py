#!/usr/bin/python

#GS_analytic_upper_limits - collects analytic upper limits and plots automagically.

import re, math,os
import matplotlib as plt 
 
def main(argv):

	usage = "GS_analytic_upper_limits -s <start frequency> -e <end frequency> [-f <file location> -b <freq band size> -o <output filename> -d <output directory>]"

	#load inputs/options
	
	startFreq = ''
	endFreq = ''
	fileLocation = '.'
	band = 0.1
	outputDir = '.'
	outFile = False

	try:
		opts, args = getopt.getopt(argv, "hs:e:f:b:o:d:", ["help", "startFreq=", "endFreq=", "files=", "band=", "outputFile=", "outputDir="])
	except getopt.GetoptError:
		print usage
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print usage
			sys.exit()
		elif opt in ("-s", "--startFreq"):
			startFreq = float(arg)
		elif opt in ("-e", "--endFreq"):
			endFreq = float(arg)
		elif opt in ("-f", "--files"):
			fileLocation = arg
		elif opt in ("-b", "--band"):
			band = float(arg)
		elif opt in ("-o", "--outFile"):
			outFile = arg
		elif opt in ("-d", "--outputDir"):
			outputDir = arg

	if not(outFile):
		outFile = "Analytic_UL_" + str(startFreq) + "_" + str(endFreq) + ".dat"

	if not(os.path.isdir(outputDir)):
		os.makedirs(outputDir)

	ULFreqs = []
	ULims = []

	freqSteps = int(round((endFreq - startFreq)/band))
	
	with open(outputDir + "/" + outFile, "w") as output:		

		for step in xrange(0,freqSteps):
		
			freq0 = startFreq + step*band

			filename = "UL_" + str(freq0) + "_band.txt"

			with open(fileLocation + "/" + filename, "r") as f:
				data = f.readlines()[-3;-2]
	
			m = re.search('(?<=h0=)\d.\d+e-\d+', data[0])

			band = {}
			band['freq'] = freq0
			band['UL'] = float(m.group(0))
	
			output.write(str(band['freq']) + " " + str(band['UL'])+"\n"	
	
			ULFreqs.append(freq0)
			ULims.append(float(m.group(0))		

if __name__ == "__main__":
	main(sys.argv[1:])
