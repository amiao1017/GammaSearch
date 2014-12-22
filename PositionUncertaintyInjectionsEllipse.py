#!/usr/bin/python

from __future__ import division
import sys, getopt, os, ConfigParser, subprocess, random, math, array

def main(argv):

	usage = "PositionUncertaintyInjections -c <config file>"

	#get options from command line

	try:
		opts, args = getopt.getopt(argv, "hc:", ["help", "configFile="])
	except getopt.GetoptError:
		print usage
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print usage
			sys.exit()
		elif opt in ("-c", "--configFile"):
			configFile = arg

	#read from config file

	try:
		config = ConfigParser.ConfigParser()
		config.read(configFile)
	except:
		sys.stderr.write("Cannot import Config File " + configFile + ", exiting...\n")
		sys.exit(1)

	Vars = {}

	try:
		Vars['sourceNumber'] = int(config.get("InjVars","Source"))
		sourceNumber = Vars['sourceNumber']
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
		Vars['Semimajor'] = float(config.get("InjVars", "Semimajor"))
	except:
		sys.stderr.write("Cannot read Semimajor\n")
		sys.exit(1)

	try:
		Vars['Semiminor'] = float(config.get("InjVars", "Semiminor"))
	except:
		sys.stderr.write("Cannot read Semiminor\n")
		sys.exit(1)
		
	try:
		Vars['Semiangle'] = float(config.get("InjVars", "Semiangle"))
	except:
		sys.stderr.write("Cannot read Semiangle\n")
		sys.exit(1)

	try:
		Vars['SFTlocation'] = config.get("InjVars","InputData")
	except:
		sys.stderr.write("Cannot read SFTlocation\n")
		sys.exit(1)

	try:
		Vars['Tau'] = float(config.get("InjVars","Age"))
		TauSecs = Vars['Tau']*24*3600*365
	except:
		sys.stderr.write("Cannot read Tau\n")
		sys.exit(1)

	try:
		Vars['m'] = float(config.get("InjVars","Mismatch"))
	except:
		sys.stderr.write("Cannot read m\n")
		sys.exit(1)

	try:
		Vars['startTime'] = float(config.get("InjVars","StartTime"))
	except:
		sys.stderr.write("Cannot read tStartGPS\n")
		sys.exit(1)

	try:
		Vars['tObs'] = float(config.get("InjVars","SearchTime"))
		Vars['endTime'] = Vars['startTime'] + Vars['tObs']
	except:
		sys.stderr.write("Cannot read tObs\n")
		sys.exit(1)

	try:
		Vars['2FThresh'] = float(config.get("InjVars","2F"))
	except:
		sys.stderr.write("Cannot read 2FThresh\n")
		sys.exit(1)

	# Ephemeris properties
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

	Vars['h0Test'] = 0.5

	injectionDag = "PUn_Ellipse_" + str(sourceNumber) + "_Injections.dag"
	searchDag = "PUn_Ellipse_" + str(sourceNumber) + "_Searches.dag"

	outputLocation = "PUn_Ellipse_"+str(sourceNumber)
	
	if not(os.path.isdir(outputLocation)):
		os.makedirs(outputLocation)

	MFDlocation = outputLocation + "/FakeData"
	CFSlocation = outputLocation + "/CFS"

	if not(os.path.isdir(MFDlocation)):
		os.makedirs(MFDlocation)
	if not (os.path.isdir(CFSlocation)):
		os.makedirs(CFSlocation)
		
	MFDsubFile = "PUn_Ellipse_Injections.sub"
	CFSsubFile = "PUn_Ellipse_Searches.sub"

	with open(MFDsubFile, "w") as f:
		f.write("universe=vanilla\n")
		f.write("executable = /usr/bin/lalapps_Makefakedata_v4\n")
		f.write("arguments = $(argList)\n")
		f.write("log = "+outputLocation+"/MFD_log.txt\n")
		f.write("error = " + outputLocation+"/MFD_error.txt\n")
		f.write("output = " + outputLocation+"/MFD_output.txt\n")
		f.write("notification = never\n")
		f.write("queue 1\n")

	with open(CFSsubFile,"w") as f:
		f.write("universe=vanilla\n")
		f.write("executable = /usr/bin/lalapps_ComputeFStatistic_v2\n")
		f.write("arguments = $(argList)\n")
		f.write("log = "+outputLocation+"/CFS_log.txt\n")
		f.write("error = " + outputLocation+"/CFS_error.txt\n")
		f.write("output = " + outputLocation+"/CFS_output.txt\n")
		f.write("notification = never\n")
		f.write("queue 1\n")

	freqlist = (100, 120, 140, 160, 180, 200, 300, 400, 500, 600, 700, 800, 900, 1000)
	cosilist = (0,1)
	
	with open(injectionDag,"w") as MFD:

		with open(searchDag,"w") as CFS:

			for freq in freqlist:

				#generate nuisance parameters
				
				Vars['Psi'] = random.uniform(0,2*math.pi)
				Vars['Phi0'] = random.uniform(0,2*math.pi)

				#generate random frequency parameters

				Vars['FDotMin'] = -freq/TauSecs
				Vars['FDotMax'] = -freq/(6.0*TauSecs)
				FDot = Vars['FDotMin'] + (Vars['FDotMax']-Vars['FDotMin'])*random.uniform(0,1)
				Vars['FDotDotMin'] = (2*FDot*FDot)/freq
				Vars['FDotDotMax'] = (7*FDot*FDot)/freq
				FDotDot = Vars['FDotDotMin'] + (Vars['FDotDotMax']-Vars['FDotDotMin'])*random.uniform(0,1)
				
				FreqVars = array.array('d',[0,0,0])
				FreqVars[0] = freq
				FreqVars[1] = FDot
				FreqVars[2] = FDotDot

				#Calculate search box to generate smaller SFTs
				#Create array with desired tempalte spacings -- [10*df, 6*dfdot, 3*dfdotdot]
				TemplateSpacings = array.array('d',[2*math.sqrt((300*Vars['m'])/((math.pi**2)*(Vars['tObs']**2))),2*math.sqrt((6480*Vars['m'])/((math.pi**2)*(Vars['tObs']**4))),2*math.sqrt((25200*Vars['m'])/((math.pi**2)*(Vars['tObs']**6)))])

				#Use template spacings to create "search box" to search for injections
				SearchBox = array.array('d',[0,0,0])
				SearchBand = array.array('d',[0,0,0])
				SearchBox[0] = FreqVars[0] - (4.0 + random.uniform(0,1)) * TemplateSpacings[0]
				SearchBand[0] = 9 * TemplateSpacings[0]
				SearchBox[1] = FreqVars[1] - (4.0 + random.uniform(0,1)) * TemplateSpacings[1]
				SearchBand[1] = 9 * TemplateSpacings[1]
				SearchBox[2] = FreqVars[2] - (4.0 + random.uniform(0,1)) * TemplateSpacings[2]
				SearchBand[2] = 9 * TemplateSpacings[2]
		
				Vars['Padding'] = 0.2

				Vars['CFSInput'] = outputLocation + "/FakeData"

				if not(os.path.isdir(Vars['CFSInput'])):
					os.makedirs(Vars['CFSInput'])

			
				for cosi in cosilist:

					#generates MFD and writes out to injection file
					Vars['MFDFmin'] = SearchBox[0] - Vars['Padding']
					Vars['MFDFBand'] = SearchBand[0] + 2*Vars['Padding']
					Vars['MFDLogFile'] = str(Vars['CFSInput']) + "/MFD_log.txt"

					Vars['CosIota'] = cosi

					jobName =  "PUn_" + str(freq) + "_" + str(cosi)
					
					freqDir = str(math.floor(freq/10.0))
										
					MFDCmdH1 = 'VARS ' + jobName + '_H1 argList=" -s --outSFTbname=' + str(Vars['CFSInput']) + "/H1_" + str(freq) + ".sft --IFO=H1 --ephemDir=" + str(Vars['EphemPath']) + " --ephemYear=" + str(Vars['EphemYrs']) + " --fmin=" + str(Vars['MFDFmin']) + " --Band=" + str(Vars['MFDFBand']) + " --refTime=" + str(Vars['startTime']) + " --Alpha=" + str(Vars['Alpha']) + " --Delta=" + str(Vars['Delta']) + " --h0=" + str(Vars['h0Test']) + " --cosi=" + str(Vars['CosIota']) + " --psi=" + str(Vars['Psi']) + " --phi0=" + str(Vars['Phi0']) + " --Freq=" + str(FreqVars[0]) + " --f1dot=" + str(FreqVars[1]) + " --f2dot=" + str(FreqVars[2]) + " --logfile=" + str(Vars['MFDLogFile']) + " --noiseSFTs=" + str(Vars['SFTlocation']) + "/" + freqDir + "/H1_" + str(freq) + ".sft --window=None\""
					
					MFDCmdL1 = 'VARS ' + jobName + '_L1 argList=" -s --outSFTbname=' + str(Vars['CFSInput']) + "/L1_" + str(freq) + ".sft --IFO=L1 --ephemDir=" + str(Vars['EphemPath']) + " --ephemYear=" + str(Vars['EphemYrs']) + " --fmin=" + str(Vars['MFDFmin']) + " --Band=" + str(Vars['MFDFBand']) + " --refTime=" + str(Vars['startTime']) + " --Alpha=" + str(Vars['Alpha']) + " --Delta=" + str(Vars['Delta']) + " --h0=" + str(Vars['h0Test']) + " --cosi=" + str(Vars['CosIota']) + " --psi=" + str(Vars['Psi']) + " --phi0=" + str(Vars['Phi0']) + " --Freq=" + str(FreqVars[0]) + " --f1dot=" + str(FreqVars[1]) + " --f2dot=" + str(FreqVars[2]) + " --logfile=" + str(Vars['MFDLogFile']) + " --noiseSFTs=" + str(Vars['SFTlocation']) + "/" + freqDir + "/L1_" + str(freq) + ".sft  --window=None\""
					
					MFD.write('JOB ' + jobName +"_H1 " + MFDsubFile + '\n')
					MFD.write('RETRY ' + jobName +"_H1 0\n")
					MFD.write(MFDCmdH1+"\n\n")	
					
					MFD.write('JOB ' + jobName +"_L1 " + MFDsubFile + '\n')
					MFD.write('RETRY ' + jobName +"_L1 0\n")
					MFD.write(MFDCmdL1+"\n\n")			

					CFSoutputDir = CFSlocation + "/cosi_" + str(cosi) + "_freq_" + str(freq)
		
					if not(os.path.isdir(CFSoutputDir)):
						os.makedirs(CFSoutputDir)

					for step in xrange(0,1001):
	
						t = 2*math.pi*random.random()
						r = math.sqrt(random.random())
						
						Alpha = Vars['Alpha'] + r*(Vars['Semiminor']*math.cos(Vars['Semiangle'])*math.cos(t) - Vars['Semimajor']*math.sin(Vars['Semiangle'])*math.sin(t))
						Delta = Vars['Delta'] + r*(Vars['Semiminor']*math.sin(Vars['Semiangle'])*math.cos(t) + Vars['Semimajor']*math.cos(Vars['Semiangle'])*math.sin(t))
						
						jobName =  "PUn_" + str(freq) + "_" + str(cosi) + "_" + str(step)

						Vars['CFSOutput'] = CFSoutputDir + "/PUn_cosi_" + str(cosi) + "_freq_" + str(freq) + "_"+str(step)+".dat"
				
						CFS.write('JOB ' + jobName + ' ' + CFSsubFile + '\n')
						CFS.write('RETRY ' + jobName + ' 0\n')
						CFS.write("VARS " + jobName + ' argList=" --Alpha=' + str(Alpha) + ' --Delta=' + str(Delta) + ' --Freq=' + str(SearchBox[0]) + ' --f1dot=' + str(SearchBox[1]) + ' --f2dot=' + str(SearchBox[2]) + ' --FreqBand=' + str(SearchBand[0]) + ' --f1dotBand=' + str(SearchBand[1]) + ' --f2dotBand=' + str(SearchBand[2]) + ' --DataFiles=' + str(Vars['CFSInput']) + '/*.sft --NumCandidatesToKeep=100 --gridType=8 --outputFstat=' + str(Vars['CFSOutput']) + ' --outputLogfile=' + outputLocation + '/CFSlog.txt --refTime=' + str(Vars['startTime']) + ' --minStartTime=' + str(Vars['startTime']) + ' --maxEndTime=' + str(Vars['endTime']) + ' --outputSingleFstats=TRUE --metricMismatch=' + str(Vars['m']) + ' --dFreq=1e-6 --useResamp=TRUE --ephemEarth='+ str(Vars['EphemEarth']) + ' --ephemSun='+str(Vars['EphemSun'])+'"\n\n')
						

if __name__ == "__main__":
	main(sys.argv[1:])
