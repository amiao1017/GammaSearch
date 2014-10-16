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
import sys, getopt, re, os, math, ConfigParser
import numpy as np
from subprocess import call


def main(argv):
	
	usage = "GS_searchwriter -s <start frequency> -e <end frequency> -c <config file> [-o <output directory> --subFiles <sub file location>]"

	#load inputs/options
	
	startFreq = ''
	endFreq = ''	
	configFile = ''
	outputDir = False
	subFileLocation = "SubFiles"

	

	try:
		opts, args = getopt.getopt(argv, "hs:e:c:o:", ["help", "startFreq=", "endFreq=", "config=","outputDir=","subFiles="])
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
		elif opt in ("-o", "--outputDir"):
			outputDir = arg
		elif opt in ("--subFiles"):
			subFileLocation = arg

	if not(os.path.isdir(subFileLocation)):
		os.makedirs(subFileLocation)

		
	#read from config file

	try:
		config = ConfigParser.ConfigParser()
		config.read(configFile)
	except:
		sys.stderr.write("Cannot import Config File " + configFile + " exiting...\n")
		sys.exit(1)

	Vars = {}
	
	try:
		Vars['sourceNumber'] = int(config.get("InjVars","Source"))
	except:
		sys.stderr.write("Cannot read sourceNumber\n")
		sys.exit(1)
	
	try:
		Vars['Alpha'] = float(config.get("InjVars","Alpha"))
	except:	
		sys.stderr.write("Cannot read Alpha\n")
		sys.exit(1)
		
	try:
		Vars['Delta'] = float(config.get("InjVars","Delta"))
	except:
		sys.stderr.write("Cannot read Delta\n")
		sys.exit(1)

	try:
		Vars['Semimajor'] = float(config.get("InjVars","Semimajor"))
	except:
		sys.stderr.write("Cannot read Semimajor\n")
		sys.exit(1)
	
	try:
		Vars['Semiminor'] = float(config.get("InjVars","Semiminor"))
	except:
		sys.stderr.write("Cannot read Semiminor\n")
		sys.exit(1)

	try:
		Vars['Semiangle'] = float(config.get("InjVars","Semiangle"))
	except:
		sys.stderr.write("Cannot read Semiangle\n")
		sys.exit(1)

	try:
		Vars['resConstant'] = float(config.get("InjVars","resConstant"))
	except:
		sys.stderr.write("Cannot read resConstant\n")
		sys.exit(1)

	try:
		Vars['Band'] = float(config.get("InjVars", "band"))
		band = Vars['Band']
	except:
		sys.stderr.write("Cannot read band\n")
		sys.exit(1)

	try:
		Vars['H1SFTlocation'] = config.get("InjVars","H1InputData")
	except:
		sys.stderr.write("Cannot read H1SFTlocation\n")
		sys.exit(1)

	try:
		Vars['L1SFTlocation'] = config.get("InjVars","L1InputData")
	except:
		sys.stderr.write("Cannot read L1SFTlocation\n")
		sys.exit(1)
	
	try:
		Vars['Tau'] = float(config.get("InjVars","Age"))
		Vars['Tau'] = Vars['Tau']*24*365*3600
	except:
		sys.stderr.write("Cannot read Tau\n")
		sys.exit(1)
	
	try:
		Vars['m'] = float(config.get("InjVars","Mismatch"))
	except:
		sys.stderr.write("Cannot read m\n")
		sys.exit(1)
	
	try:
		Vars['lowestFreq'] = float(config.get("InjVars","lowestF"))
	except:
		sys.stderr.write("Cannot read lowestFreq\n")
		sys.exit(1)

	try:
		Vars['startTime'] = float(config.get("InjVars","StartTime"))
	except:
		sys.stderr.write("Cannot read startTime\n")
		sys.exit(1)

	try:
		Vars['searchDuration'] = float(config.get("InjVars","SearchTime"))
	except:
		sys.stderr.write("Cannot read searchDuration\n")
		sys.exit(1)

	try:
		Vars['2FThresh'] = float(config.get("InjVars", "2F"))
	except:
		sys.stderr.write("Cannot read 2FThresh\n")
		sys.exit(1)

	try:	
		Vars['EphemEarth'] = config.get("InjVars","EphemEarth")
	except:
		sys.stderr.write("Cannot read EphemEarth\n")
		sys.exit(1)
		
	try:
		Vars['EphemSun'] = config.get("InjVars","EphemSun")
	except:
		sys.stderr.write("Cannot read EphemSun\n")
		sys.exit(1)		

	Vars['endTime'] = Vars['startTime'] + Vars['searchDuration']



	freqRange = endFreq-startFreq
	freqSteps = int(round(freqRange/band))

	dagName = "GS_"+str(Vars['sourceNumber'])+"_"+str(startFreq)+"_"+ str(endFreq) + ".dag"

	if os.path.isfile(dagName):
		os.remove(dagName)

	if not(outputDir):
		outputDir = "GS_"+str(Vars['sourceNumber'])
	if not(os.path.isdir(outputDir)):
		os.makedirs(outputDir)

	outputLocation = outputDir+"/"+"GS_"+str(Vars['sourceNumber'])+"_"+str(startFreq)+"_"+str(endFreq)	
	dataDir = outputLocation+"/Data"	

	if not(os.path.isdir(outputLocation)):
		os.makedirs(outputLocation)
	if not(os.path.isdir(dataDir)):
		os.makedirs(dataDir)

	for x in xrange(0,freqSteps):
				
		freq = startFreq + x*band
		
		dataLocation = str(dataDir)+"/GS_"+str(Vars['sourceNumber'])+"_"+str(freq)

		if not(os.path.isdir(dataLocation)):
			os.makedirs(dataLocation)

		minFreq = freq - band*2
		maxFreq = freq + band*6

		#produce data files for searching using ConverttoSFTv2

		#call(["lalapps_ConvertToSFTv2", "--inputSFTs="+Vars['H1SFTlocation'], "--outputDir="+dataLocation, "--fmin="+str(minFreq), "--fmax="+str(maxFreq)])
		#call(["lalapps_ConvertToSFTv2", "--inputSFTs="+Vars['L1SFTlocation'], "--outputDir="+dataLocation, "--fmin="+str(minFreq), "--fmax="+str(maxFreq)])

		
		#calculate spindown parameters
				
		f1dot = -(freq+band)/Vars['Tau']
		f1dotBand = (6*(freq+band)-Vars['lowestFreq'])/(6*Vars['Tau'])
		
		f2dot = 7*f1dot**2/Vars['lowestFreq']
		f2dotBand = (126*(freq+band)**3 - Vars['lowestFreq']**3)/(18*Vars['Tau']**2*(freq+band)*Vars['lowestFreq'])

		resolution = Vars['resConstant']/freq
	
		count = 1
		step = 1
		j = 4	

		AlphaList = []
		DeltaList = []

		AlphaList.append(Vars['Alpha'])
		DeltaList.append(Vars['Delta'])

		while (count > 0):
			count = 0
			for x in range(0,j):
				t = 2.0*math.pi/float(j)*float(x)
				alpha_temp = Vars['Alpha'] + math.cos(Vars['Semiangle'])*resolution*step*math.cos(t) - math.sin(Vars['Semiangle'])*resolution*step*math.sin(t)
				delta_temp = Vars['Delta'] + math.sin(Vars['Semiangle'])*resolution*step*math.cos(t) + math.cos(Vars['Semiangle'])*resolution*step*math.sin(t)

				if isInErrorEllipse(Vars['Alpha'], Vars['Delta'], Vars['Semimajor'], Vars['Semiminor'], Vars['Semiangle'], alpha_temp, delta_temp):
					AlphaList.append(alpha_temp)
					DeltaList.append(delta_temp)
					count = count + 1
			j = 2*j

		#write SUB file

		subFileName = subFileLocation+"/GS_"+str(Vars['sourceNumber'])+"_"+str(freq)+".sub"

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
				jobName = "GS_"+str(Vars['sourceNumber'])+"_"+str(freq)+"_"+str(x)
				f.write("JOB "+ jobName + " " + subFileName + "\n")
				f.write("RETRY " + jobName + " 0\n")
				f.write("VARS " + jobName + ' argList=" --Alpha=' + str(AlphaList[x]) + ' --Delta=' + str(DeltaList[x]) + ' --Freq=' + str(freq) + ' --f1dot=' + str(f1dot) + ' --f2dot=' + str(f2dot) + ' --FreqBand=' + str(band) + ' --f1dotBand=' + str(f1dotBand) + ' --f2dotBand=' + str(f2dotBand) + ' --DataFiles=' + dataLocation + '/*.sft --TwoFthreshold=' + str(Vars['2FThresh']) + ' --NumCandidatesToKeep=100 --gridType=8 --outputFstat=' + outputLocation + '/GammaSearch_' + str(freq) + '_' + str(x) + '.dat --outputFstatHist=' + outputLocation + '/GammaHist_' + str(freq) + '_' + str(x) + '.dat --outputLoudest=' + outputLocation + '/GammaLoud_' + str(freq) + '_' + str(x) + '.dat --outputLogfile=' + outputLocation + '/CFSlog.txt --refTime=' + str(Vars['startTime']) + ' --minStartTime=' + str(Vars['startTime']) + ' --maxEndTime=' + str(Vars['endTime']) + ' --outputSingleFstats=TRUE --metricMismatch=' + str(Vars['m']) + ' --dFreq=1e-6 --useResamp=TRUE --ephemEarth='+ str(Vars['EphemEarth']) + ' --ephemSun='+str(Vars['EphemSun'])+'"\n')
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


