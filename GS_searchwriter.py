#!/usr/bin/python

# Searchwriter for gammasearch investigation
# J.R. Sanders Sept 2014

# Inputs:
# frequency, config file

# Output:
# dag file for searching

# load input variables from command line

# define variables to be loaded from config file

from __future__ import division
import sys, getopt, re, os, math
import numpy as np
from subprocess import call


def main(argv):
	
	usage = "GS_searchwriter -s <start frequency> -e <end frequency> -c <config file> [-b <freq band> -o <output directory> -m <mismatch> -t <tau> -l <lower search bound> --subFiles <sub file location>]"

	#load inputs/options
	
	startFreq = ''
	endFreq = ''	
	configFile = ''
	outputDir = False
	subFileLocation = "SubFiles"

	
	band = 0.1
	tau = 200.0*365*24*3600
	mismatch = 0.2
	lowestFreq=50.0
	resConstant = 0.83
	TwoFThreshold = 40
	startTime = 970840605
	endTime = 971272605

	try:
		opts, args = getopt.getopt(argv, "hs:e:c:b:o:t:m:l:", ["help", "startFreq=", "endFreq=", "config=", "band=","outputDir=","tau=","mismatch=", "lowestFreq=", "subFiles="])
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
		elif opt in ("-c", "--config"):
			configFile = arg
		elif opt in ("-b", "--band"):
			band = float(arg)	
		elif opt in ("-o", "--outputDir"):
			outputDir = arg
		elif opt in ("-t", "--tau"):
			tau = float(arg)*365*24*3600
		elif opt in ("-m", "--mismatch"):
			mismatch = float(arg)
		elif opt in ("-l", "--lowestFreq"):
			lowestFreq = float(arg)
		elif opt in ("--subFiles"):
			subFileLocation = arg

	if not(os.path.isdir(subFileLocation)):
		os.makedirs(subFileLocation)

		
	#read from config file

	configData = []

	with open(configFile, 'r') as f:
		for line in f:
			m = re.search('(?<==).+',line)
			configData.append(m.group(0))
	

	sourceNumber = configData[0]
	Alpha = float(configData[1])
	Delta = float(configData[2])
	Semimajor = float(configData[3])
	Semiminor = float(configData[4])
	Semiangle = float(configData[5])
	H1SFTlocation = configData[6]
	L1SFTlocation = configData[7]

	freqRange = endFreq-startFreq
	freqSteps = int(round(freqRange/band))

	dagName = "GS_"+str(sourceNumber)+"_"+str(startFreq)+".dag"

	if os.path.isfile(dagName):
		os.remove(dagName)

	if not(outputDir):
		outputDir = "GS_"+str(sourceNumber)
	if not(os.path.isdir(outputDir)):
		os.makedirs(outputDir)

	outputLocation = outputDir+"/"+"GS_"+str(sourceNumber)+"_"+str(startFreq)	
	dataDir = outputLocation+"/Data"	

	if not(os.path.isdir(outputLocation)):
		os.makedirs(outputLocation)
	if not(os.path.isdir(dataDir)):
		os.makedirs(dataDir)

	for x in xrange(0,freqSteps):
				
		freq = startFreq + x*band
		
		dataLocation = str(dataDir)+"/GS_"+str(sourceNumber)+"_"+str(freq)

		if not(os.path.isdir(dataLocation)):
			os.makedirs(dataLocation)

		minFreq = freq - band*2
		maxFreq = freq + band*6

		#produce data files for searching using ConverttoSFTv2

		#call(["lalapps_ConvertToSFTv2", "--inputSFTs="+H1SFTlocation, "--outputDir="+dataLocation, "--fmin="+str(minFreq), "--fmax="+str(maxFreq)])
		#call(["lalapps_ConvertToSFTv2", "--inputSFTs="+L1SFTlocation, "--outputDir="+dataLocation, "--fmin="+str(minFreq), "--fmax="+str(maxFreq)])

		
		#calculate spindown parameters
				
		f1dot = -(freq+band)/tau
		f1dotBand = (6*(freq+band)-lowestFreq)/(6*tau)
		
		f2dot = 7*f1dot**2/lowestFreq
		f2dotBand = (126*(freq+band)**3 - lowestFreq**3)/(18*tau**2*(freq+band)*lowestFreq)

		resolution = resConstant/freq
	
		count = 1
		step = 1
		j = 4	

		AlphaList = []
		DeltaList = []

		AlphaList.append(Alpha)
		DeltaList.append(Delta)

		while (count > 0):
			count = 0
			for x in range(0,j):
				t = 2.0*math.pi/float(j)*float(x)
				alpha_temp = Alpha + math.cos(Semiangle)*resolution*step*math.cos(t) - math.sin(Semiangle)*resolution*step*math.sin(t)
				delta_temp = Delta + math.sin(Semiangle)*resolution*step*math.cos(t) + math.cos(Semiangle)*resolution*step*math.sin(t)

				if isInErrorEllipse(Alpha, Delta, Semimajor, Semiminor, Semiangle, alpha_temp, delta_temp):
					AlphaList.append(Alpha)
					DeltaList.append(Delta)
					count = count + 1
			j = 2*j

		#write SUB file

		subFileName = subFileLocation+"/GS_"+str(sourceNumber)+"_"+str(freq)+".sub"

		with open(subFileName,"w") as f:
			f.write("universe=vanilla\n")
			f.write("executable = /usr/bin/lalapps_ComputeFStatistic_v2\n")
			f.write("arguments = $(argList)\n")
			f.write("log = "+outputLocation+"/GS_log.txt\n")
			f.write("error = " + outputLocation+"/GS_error.txt\n")
			f.write("output = " + outputLocation+"/GS_output.txt\n")
			f.write("notification = never\n")
			f.write("queue 1\n")
			
		#write DAG
		with open(dagName, "a") as f:
			for x in range(0, len(AlphaList)):
				jobName = "GS_"+str(sourceNumber)+"_"+str(freq)+"_"+str(x)
				f.write("JOB "+ jobName + " " + subFileName + "\n")
				f.write("RETRY " + jobName + " 0\n")
				f.write("VARS " + jobName + ' argList=" --Alpha=' + str(AlphaList[x]) + ' --Delta=' + str(DeltaList[x]) + ' --Freq=' + str(freq) + ' --f1dot=' + str(f1dot) + ' --f2dot=' + str(f2dot) + ' --f1dotBand=' + str(f1dotBand) + ' --f2dotBand=' + str(f2dotBand) + ' --DataFiles=' + dataLocation + '/*.sft --TwoFthreshold=' + str(TwoFThreshold) + ' --NumCandidatesToKeep=100 --gridType=8 --outputFstat=' + outputLocation + '/GammaSearch_' + str(freq) + '_' + str(x) + '.dat --outputFstatHist=' + outputLocation + '/GammaHist_' + str(freq) + '_' + str(x) + '.dat --outputLoudest=' + outputLocation + '/GammaLoud_' + str(freq) + '_' + str(x) + '.dat --outputLogfile=' + outputLocation + '/CFSlog.txt --refTime=' + str(startTime) + ' --minStartTime=' + str(startTime) + ' --maxEndTime=' + str(endTime) + ' --outputSingleFstats=TRUE --metricMismatch=' + str(mismatch) + ' --dFreq=1e-6 --useResamp=TRUE --ephemEarth=/mnt/qfs2/jaclyn.sanders/earth00-19-DE405.dat.gz --ephemSun=/mnt/qfs2/jaclyn.sanders/sun00-19-DE405.dat.gz"\n')
				f.write("\n")

	
		

def isInErrorEllipse(Alpha0, Delta0, Semimajor, Semiminor, Semiangle, AlphaTest, DeltaTest):

	#determines if a point is in the 120% error ellipse using definition of ellipse.

	a = 1.2*Semimajor
	b = 1.2*Semiminor

	focalDistance = math.sqrt(a**2 - b**2)
	c1_x = Alpha0 - math.sin(Semiangle)*focalDistance
	c1_y = Delta0 + math.cos(Semiangle)*focalDistance
	c2_x = Alpha0 + math.sin(Semiangle)*focalDistance
	c2_y = Delta0 - math.cos(Semiangle)*focalDistance

	focalDistance_1 = math.sqrt((AlphaTest - c1_x)**2 + (DeltaTest - c1_y)**2)
	focalDistance_2 = math.sqrt((AlphaTest - c2_x)**2 + (DeltaTest - c2_y)**2)

	if (focalDistance_1 + focalDistance_2 < 2*a):
		return 1
	else:
		return 0

if __name__ == "__main__":
	main(sys.argv[1:])


