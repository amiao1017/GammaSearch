#!/usr/bin/python

import os

lowerFrequencyBound = 50.0
bandSize = 0.1

subFileName = "MasterSFTBanding.sub"
dagFileName = "MasterSFTBanding.dag"
H1SFTLocation = "/home/jaclyn.sanders/SFTs/H1/*.sft"
L1SFTLocation = "/home/jaclyn.sanders/SFTs/L1/*.sft"	
outputLocation = "/home/jaclyn.sanders/BandedSFTs"
#outputLocation = "BandedSFTs"

if not(os.path.isdir(outputLocation)):
	os.makedirs(outputLocation)

with open(subFileName, "w") as f:
	f.write("universe = vanilla\n")
	f.write("executable = /usr/bin/lalapps_ConvertToSFTv2\n")
	f.write("arguments= $(argList)\n")
	f.write("log = MasterSFTLog.txt\n")
	f.write("error = MasterSFTError.txt\n")
	f.write("output = MasterSFTOutput.txt\n")
	f.write("notification = never\n")
	f.write("queue 1\n")

with open(dagFileName,"w") as f:

	for x in xrange(0,95):
		
		tenHz = lowerFrequencyBound + x*10
		tenHzDir = outputLocation + "/" + str(tenHz)	

		if not(os.path.isdir(tenHzDir)):
			os.makedirs(tenHzDir)	

		for y in xrange(0,100):

			freqBand = tenHz + y*0.1
			minFreq = freqBand - 2*bandSize
			maxFreq = freqBand + 6*bandSize
		
			H1jobname = 'H1_' + str(freqBand)
			L1jobname = 'L1_' + str(freqBand)
	
			H1filename = H1jobname + '.sft'
			L1filename = L1jobname + '.sft' 

			f.write("JOB " + H1jobname + " " + subFileName + "\n")
			f.write("RETRY " + H1jobname + " 0\n")
			f.write("VARS " + H1jobname + ' argList=" --inputSFTs=' + H1SFTLocation + ' --outputSingleSFT=' + H1filename + ' --outputDir=' + tenHzDir + ' --fmin=' + str(minFreq) + ' --fmax=' + str(maxFreq) + '"\n')
			f.write("\n")

			f.write("JOB " + L1jobname + " " + subFileName + "\n")
			f.write("RETRY " + L1jobname + " 0\n")
			f.write("VARS " + L1jobname + ' argList=" --inputSFTs=' + L1SFTLocation + ' --outputSingleSFT=' + L1filename + ' --outputDir=' + tenHzDir + ' --fmin=' + str(minFreq) + ' --fmax=' + str(maxFreq) + '"\n')
			f.write("\n")

			


			



