#!/usr/bin/python

#GS_2F_to_UL - collects ComputeFStatistic_v2 outputs and sets up dags to run analytical upper limits. 

from __future__ import division
import sys, getopt, re, os, math, ConfigParser

def main(argv):

	usage = "GS_2F_to_UL -s <start frequency> -e <end frequency> -c <config file> -f <CFS output location> [-o <output filename> -d <output directory>]"

	#load inputs/options

	startFreq = ''
	endFreq = ''
	fileLocation = '.'
	outFile = False
	outputDir = False
	
	loudest2F = []

	try:
		opts, args = getopt.getopt(argv, "hs:e:f:c:o:d:", ["help", "startFreq=", "endFreq=", "files=" "configFile=", "outFile=", "outputDir="])
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
		elif opt in ("-c", "--configFile"):
			configFile = arg
		elif opt in ("-f", "--files"):
			fileLocation = arg
		elif opt in ("-o", "--outFile"):
			outFile = arg
		elif opt in ("-d", "--outputDir"):
			outputDir = arg

	Vars = {}

	try:
		config = ConfigParser.ConfigParser()
		config.read(configFile)
	except:
		sys.stderr.write("Cannot import Config File " + configFile + " exiting... \n")
		sys.exit(2)

	try:
		Vars['Band'] = float(config.get("InjVars","band"))
		band = Vars['Band']
	except:
		sys.stderr.write("Cannot read band\n")
		sys.exit(1)

	try:
		Vars['sourceNumber'] = int(config.get("InjVars","Source"))
		sourceNumber = Vars['sourceNumber']
	except:
		sys.stderr.write("Cannot read sourceNumber\n")
		sys.exit(1)

	try:
		Vars['SFTlocation'] = int(config.get("InjVars","InputData"))
	except:
		sys.stderr.write("Cannot read SFTlocation\n")
		sys.exit(1)

	try:
		Vars['EphemPath'] = config.get("InjVars","EphemPath")
	except:
		sys.stderr.write("Cannot read EphemPath\n")
		sys.exit(1)

	try:
		Vars['EphemYrs'] = config.get("InjVars","EphemYears")
	except:
		sys.stderr.write("Cannot read EphemYrs\n")
		sys.exit(1)

	if not(outFile):
		outFile = "GS_UL_" + str(sourceNumber) + "_" + str(startFreq) + "_" + str(endFreq) + ".dag"
	
	if not(outputDir):
		outputDir = "GS_aUL_" + str(sourceNumber)

	if not(os.path.isdir(outputDir)):
		os.makedirs(outputDir)

	freqSteps = int(round((endFreq-startFreq)/band))

	with open(outFile, "w") as output:

		with open(outputDir + "/GS_UL_" +str(sourceNumber) + "_" + str(startFreq) + "_" + str(endFreq) + "_record.txt", "w") as record:

			record.write("f0 Frequency Search RA Dec Fstat\n")

			for step in xrange(0,freqSteps):

				Fstatlist = [] 
				freq = startFreq + step*band
				freqDir = str(math.floor(freq/10))
				i = 0
				maxFstat = 0
				maxFstatInd = 0

				filename = fileLocation + "/GammaSearch_" + str(freq) + "_" + str(i) + ".dat"
				filepattern = SFTlocation + "/" + freqDir "/*_" + str(freq) + ".sft"
				
				while os.path.isfile(filename):						

					with open(filename, 'r') as input:
						data = input.readlines()[20:-1]

					for line in data:
						line = line.strip()
						columns = line.split()
						source = {}
						source['freq'] = columns[0]
						source['ra'] = columns[1]
						source['dec'] = columns[2]
						source['Fstat'] = columns[6]
						source['FstatH1'] = columns[7]
						source['FstatL1'] = columns[8]
						source['f0'] = str(freq)
						source['searchno'] = str(i)

						if FStatVeto(source['Fstat'], source['FstatH1'], source['FstatL1']) and (source['Fstat'] > maxFstat):
							Fstatlist.append(source)
							maxFstat = source['Fstat']
							maxFstatInd = int(source['searchno'])
							break							
												
					i = i + 1

					filename = fileLocation + "/GammaSearch_" + str(freq) + "_" + str(i) + ".dat"			
					
	
	
				if Fstatlist:


					record.write(Fstatlist[maxFstatInd]['f0'] + " " + Fstatlist[maxFstatInd]['freq'] + " " + Fstatlist[maxFstatInd]['searchno'] + " " + Fstatlist[maxFstatInd]['ra'] + " " + Fstatlist[maxFstatInd]['dec'] + " " + Fstatlist[maxFstatInd]['Fstat'] + "\n")	

					outputSubDir = outputDir + "/" + str(math.floor(freq/10))

					if not(os.path.isdir(outputSubDir)):
						os.makedirs(outputSubDir)

					outputfilename = outputSubDir + "/UL_"+ str(sourceNumber) + "_" + str(freq) + "_band.txt"
	
					output.write("JOB " + outputfilename + " AnalyticUL.sub\n")
					output.write("RETRY " + outputfilename + " 0\n")
					output.write("VARS " + outputfilename + ' argList=" -a ' + Fstatlist[maxFstatInd]['ra'] + " -d " + Fstatlist[maxFstatInd]['dec'] + " -f " + Fstatlist[maxFstatInd]['f0'] + " -b " + str(band) + " -F " + Fstatlist[maxFstatInd]['Fstat'] + " -D " + filepattern + " -E " + Vars['EphemPath'] +" -y " + Vars['EphemYrs'] + " -o " + outputfilename + '"\n')
					output.write("\n")

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

	
