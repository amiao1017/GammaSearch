#!/usr/bin/python

#GS_analytic_upper_limits - collects analytic upper limits and plots automagically.

import re, math,os, getopt
import matplotlib.pyplot as plt 
from pylab import *
 
def main(argv):

	usage = "GS_analytic_upper_limits -s <start frequency> -e <end frequency> [-n <source number> -p (plot flag) -f <file location> -b <freq band size> -o <output filename> -d <output directory>]"

	#load inputs/options
	
	startFreq = ''
	endFreq = ''
	fileLocation = '.'
	band = 0.1
	outputDir = '.'
	outFile = False
	plotResults = False
	sourceNumber = "880"

	try:
		opts, args = getopt.getopt(argv, "hps:e:f:b:o:d:n:", ["help", "plot", "startFreq=", "endFreq=", "files=", "band=", "outputFile=", "outputDir=", "sourceNumber="])
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
		elif opt in ("-p", "--plot"):
			plotResults = True
		elif opt in ("-n", "--sourceNumber"):
			sourceNumber = arg

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
				data = f.readlines()[-3:-2]
	
			m = re.search('(?<=h0=)\d.\d+e-\d+', data[0])

			ULband = {}
			ULband['freq'] = freq0
			ULband['UL'] = float(m.group(0))
	
			output.write(str(ULband['freq']) + " " + str(ULband['UL'])+"\n")	
	
			ULFreqs.append(freq0)
			ULims.append(float(m.group(0)))		
	

	if plotResults:
		fig = plt.figure(figsize=(8,6))
		ax = fig.add_subplot(1,1,1)
		ax.plot(ULFreqs, ULims, 'ro')
		ax.set_xlabel('Frequency (Hz)')
		ax.set_ylabel('h0 (95% upper limit)')
		ax.set_title("Analytic Upper Limits for source " + sourceNumber, fontsize="large") 
		plt.savefig('Analytic_UL_' + str(startFreq) + "_" + str(endFreq) + ".png")
		plt.show()
	

if __name__ == "__main__":
	main(sys.argv[1:])
