#!/usr/bin/python

# GS_UL_injection_writer - writes injections/searches for verifying analytic upper limits!

from __future__ import division
import sys, getopt, re, os, math, random, subprocess, array, ConfigParser
import numpy as np

def main(argv):

# four sets of 250 injections made: strength 0.9h, 0.95h, 1.05h, 1.10h.

	usage = "GS_UL_injection_writer -c <config file> -r <record file> -s <start frequency> -e <end frequency> [--subFiles <sub file location>]"

	nInjections = 2
	outputDir = False

	try:
		opts, args = getopt.getopt(argv, "hc:r:s:e:", ["help", "configFile=","recordFile=", "startFreq=", "endFreq=", "subFiles="])
	except getopt.GetoptError:
		print usage
		sys.exit(2)
	
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print usage
			sys.exit()
		elif opt in ("-c", "--configFile"):
			configfile = arg
		elif opt in ("-r", "--recordFile"):
			recordfile = arg
		elif opt in ("-s", "--startFreq"):
			startFreq = float(arg)
		elif opt in ("-e", "--endFreq"):
			endFreq = float(arg)
		elif opt in ("--subFiles"):
			subFileLocation = arg

	try:
		recordfile
	except:
		sys.stderr.write("Invalid record file " + recordfile)
		sys.exit(1)

	search_record = np.loadtxt(recordfile, skiprows=1)

	try:
		config = ConfigParser.ConfigParser()
		config.read(configfile)
	except:
		sys.stderr.write("Cannot import Config file " + configfile + " exiting...\n")
		sys.exit(1)

	#Variables structure/dictionary

	Vars = {}

	#load inputs/options

	Vars['FMin'] = startFreq
 
	Vars['SearchBand'] = 1
	Vars['FBand'] = 0.1
	sourceNumber = 880

	#Numerical search properties
	
	try: 
		Vars['Tau'] = float(config.get("InjVars","Age"))
	except:
		sys.stderr.write("Cannot read Tau\n")
		sys.exit(1)

	try:
		Vars['m'] = float(config.get("InjVars","Mismatch"))
	except:
		sys.stderr.write("Cannot read m\n")
		sys.exit(1)

	try:
		Vars['tStartGPS'] = float(config.get("InjVars","StartTime"))
	except:
		sys.stderr.write("Cannot read tStartGPS\n")
		sys.exit(1)

	try:
		Vars['tObs'] = float(config.get("InjVars","SearchTime"))
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

	try:
		Vars['H1InputData'] = config.get("InjVars","H1InputData")
	except:
		sys.stderr.write("Cannot read H1InputData\n")
		sys.exit(1)

	try:
		Vars['L1InputData'] = config.get("InjVars","L1InputData")
	except:
		sys.stderr.write("Cannot read L1InputData\n")
		sys.exit(1)
			
	# will have to have some sort of output file/directory handling here. placeholders for the moment though!

	injectionDag = "GS_UL_" + str(sourceNumber) + "_Injections_" + str(startFreq) + "_" + str(endFreq) + ".dag"
	searchDag = "GS_UL_" + str(sourceNumber) + "_Searches_" + str(startFreq) + "_" + str(endFreq) + ".dag"
	injectionRecord = "GS_UL_" + str(sourceNumber) + "_Injection_Record_" + str(startFreq) + "_" + str(endFreq) + ".txt"

	if not(outputDir):
		outputDir = "GS_UL_"+str(sourceNumber)
	if not(os.path.isdir(outputDir)):
		os.makedirs(outputDir)

	outputLocation = outputDir+"/"+"GS_UL_"+str(sourceNumber)+"_"+str(startFreq)+"_"+str(endFreq)
	MFDInputs = outputLocation+"/MFD_Inputs"

	if not(os.path.isdir(outputLocation)):
		os.makedirs(outputLocation)
	if not(os.path.isdir(MFDInputs)):
		os.makedirs(MFDInputs)

        CFSsubFileName = subFileLocation+"/GS_UL_Injection_CFS_"+str(sourceNumber)+"_"+str(startFreq)+".sub"
        MFDsubFileName = subFileLocation+"/GS_UL_Injection_MFD_"+str(sourceNumber)+"_"+str(startFreq)+".sub"

	with open(CFSsubFileName,"w") as f:
		f.write("universe=vanilla\n")
		f.write("executable = /usr/bin/lalapps_ComputeFStatistic_v2\n")
		f.write("arguments = $(argList)\n")
		f.write("log = "+outputLocation+"/GS_log.txt\n")
		f.write("error = " + outputLocation+"/GS_error.txt\n")
		f.write("output = " + outputLocation+"/GS_output.txt\n")
		f.write("notification = never\n")
		f.write("queue 1\n")

	with open(MFDsubFileName,"w") as f:
		f.write("universe=vanilla\n")
		f.write("executable = /usr/bin/lalapps_Makefakedata_v4\n")
		f.write("arguments = $(argList)\n")
		f.write("log = "+outputLocation+"/GS_MFD_log.txt\n")
		f.write("error = " + outputLocation+"/GS_MFD_error.txt\n")
		f.write("output = " + outputLocation+"/GS_MFD_output.txt\n")
		f.write("notification = never\n")
		f.write("queue 1\n")


	freqRange = endFreq-startFreq
	freqSteps = int(round(freqRange/Vars['FBand']))

	searchSteps = int(round(freqRange/Vars['SearchBand']))

	freqList = np.zeros((freqSteps))
	dataLocs = []
		
	for x in range(0,freqSteps):
		Vars['FMin'] = startFreq + x*Vars['FBand']
		freqList[x] = Vars['FMin']
		dataLocation = MFDInputs + "/Data_" + str(Vars['FMin'])
		dataLocs.append(dataLocation)
	
		if not(os.path.isdir(dataLocation)):
			os.makedirs(dataLocation)

		Vars['H1MFDInput'] = dataLocation + "/H1"
		Vars['L1MFDInput'] = dataLocation + "/L1"

		if not(os.path.isdir(Vars['H1MFDInput'])):
			os.makedirs(Vars['H1MFDInput'])
		if not(os.path.isdir(Vars['L1MFDInput'])):
			os.makedirs(Vars['L1MFDInput'])

   		Vars['BandFMin'] = Vars['FMin'] - Vars['FBand']
   		Vars['BandFMax'] = Vars['FMin'] + 3*Vars['FBand']
    		BandingCmdH1 = 'lalapps_ConvertToSFTv2 --inputSFTs=' + str(Vars['H1InputData']) + ' --outputDir=' + str(Vars['H1MFDInput']) + ' --fmin=' + str(Vars['BandFMin']) + ' --fmax=' + str(Vars['BandFMax'])
    		BandingCmdL1 = 'lalapps_ConvertToSFTv2 --inputSFTs=' + str(Vars['L1InputData']) + ' --outputDir=' + str(Vars['L1MFDInput']) + ' --fmin=' + str(Vars['BandFMin']) + ' --fmax=' + str(Vars['BandFMax']) 
   		#print 'Creating small-band SFTs...' 
    		#print BandingCmdH1
    		#subprocess.call(BandingCmdH1, shell=True)
    		#print BandingCmdL1
    		#subprocess.call(BandingCmdL1, shell=True)
    		#print '...done.'
		
	Vars['FMin'] = startFreq



	h0_test = (0.9, 0.95, 1.05, 1.10)
	TauSecs = Vars['Tau']*365*86400
	

	with open(injectionDag, "w") as MFD:
	
		with open(searchDag, "w") as CFS: 

			with open(injectionRecord, "w") as record:

				record.write('StrainFactor Injection Frequency FrequencyBin SearchPos Alpha Delta\n')

				for strainfactor in h0_test:
					
					strain_output = outputLocation + "/strain_" + str(strainfactor)

					if not(os.path.isdir(strain_output)):
						os.makedirs(strain_output)

					
					for search in range(0, searchSteps):
		

						for i in xrange(0,nInjections):
					
							#generate random nuisance parameters
							Vars['CosIota'] = random.uniform(-1,1)
							Vars['Psi'] = random.uniform(0,2*math.pi)
							Vars['Phi0'] = random.uniform(0,2*math.pi)

							#generate random frequency parameters
							Freq0 = Vars['FMin'] + Vars['SearchBand']*search
							Freq = Vars['FMin'] + Vars['SearchBand']*(search + random.uniform(0,1))
						
							bindiff = search_record[:,0]-Freq
							binlist = bindiff[bindiff<0]
							searchindex = len(binlist)-1

							datalocdiff = freqList[:] - Freq
							dataloclist = datalocdiff[datalocdiff<0]
							dataLocation = dataLocs[len(dataloclist)-1]
						
							# outputLocation/strainfactor_n/test_i		

							Vars['CFSInput'] = strain_output + "/test_" + str(i)
		
							if not(os.path.isdir(Vars['CFSInput'])):
								os.makedirs(Vars['CFSInput'])
									
							Vars['SearchNo'] = search_record[searchindex,3]
							Vars['Alpha'] = search_record[searchindex,4]
							Vars['Delta'] = search_record[searchindex,5]
							Vars['h0Test'] = search_record[searchindex,1]*strainfactor
											
	
							Vars['FDotMin'] = -Freq/TauSecs
							Vars['FDotMax'] = -Freq/(6.0*TauSecs)
							FDot = Vars['FDotMin'] + (Vars['FDotMax']-Vars['FDotMin'])*random.uniform(0,1)
							Vars['FDotDotMin'] = (2*FDot*FDot)/Freq
							Vars['FDotDotMax'] = (7*FDot*FDot)/Freq
							FDotDot = Vars['FDotDotMin'] + (Vars['FDotDotMax']-Vars['FDotDotMin'])*random.uniform(0,1)
							FreqVars = array.array('d',[0,0,0])
							FreqVars[0] = Freq
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

							#generates MFD and writes out to injection file

							Vars['MFDFmin'] = SearchBox[0] - Vars['Padding']
							Vars['MFDFBand'] = SearchBand[0] + 2*Vars['Padding']
							Vars['MFDLogFile'] = str(Vars['CFSInput']) + "/MFD_log.txt"

							jobName = "GS_UL_Injection_"+ str(Freq0) + "_" + str(strainfactor)+ "_" + str(i)
							
							MFDCmdH1 = 'VARS ' + jobName + '_H1 argList= "--outSFTbname=' + str(Vars['CFSInput']) + ' --IFO=H1 --ephemDir=' + str(Vars['EphemPath']) + ' --ephemYear=' + str(Vars['EphemYrs']) + ' --fmin=' + str(Vars['MFDFmin']) + ' --Band=' + str(Vars['MFDFBand']) + ' --refTime=' + str(Vars['tStartGPS']) + ' --RA=' + str(Vars['Alpha']) + ' --Dec=' + str(Vars['Delta']) + ' --h0=' + str(Vars['h0Test']) + ' --cosi=' + str(Vars['CosIota']) + ' --psi=' + str(Vars['Psi']) + ' --phi0=' + str(Vars['Phi0']) + ' --Freq=' + str(FreqVars[0]) + ' --f1dot=' + str(FreqVars[1]) + ' --f2dot=' + str(FreqVars[2]) + ' --logfile=' + str(Vars['MFDLogFile']) + ' --noiseSFTs=' + dataLocation + '/H1/*.sft"'

   							MFDCmdL1 = 'VARS ' + jobName + '_L1 argList= "--outSFTbname=' + str(Vars['CFSInput']) + ' --IFO=L1 --ephemDir=' + str(Vars['EphemPath']) + ' --ephemYear=' + str(Vars['EphemYrs']) + ' --fmin=' + str(Vars['MFDFmin']) + ' --Band=' + str(Vars['MFDFBand']) + ' --refTime=' + str(Vars['tStartGPS']) + ' --RA=' + str(Vars['Alpha']) + ' --Dec=' + str(Vars['Delta']) + ' --h0=' + str(Vars['h0Test']) + ' --cosi=' + str(Vars['CosIota']) + ' --psi=' + str(Vars['Psi']) + ' --phi0=' + str(Vars['Phi0']) + ' --Freq=' + str(FreqVars[0]) + ' --f1dot=' + str(FreqVars[1]) + ' --f2dot=' + str(FreqVars[2]) + ' --noiseSFTs=' + dataLocation + '/L1/*.sft"'
						
										
							MFD.write('JOB ' + jobName + '_H1 ' + MFDsubFileName + '\n')
							MFD.write('RETRY ' + jobName + '_H1 0\n')
							MFD.write(MFDCmdH1 + "\n\n")
							MFD.write('JOB ' + jobName + '_L1 ' + MFDsubFileName + '\n')
							MFD.write('RETRY ' + jobName + '_L1 0\n')
							MFD.write(MFDCmdL1 + "\n\n")
						
							#generates CFS and writes out to CFS dag
	
							Vars['CFSOutput'] = strain_output + "/CFS_Out_Test_"+str(i)+".dat"
							Vars['CFSHist'] = strain_output + "/CFS_Hist_Test_"+str(i)+".dat"
							Vars['CFSTopList'] = strain_output+"/CFS_Max_Test_"+str(i)+".dat"

						

							CFSv2Cmd = 'VARS ' + jobName + ' arglist=" --RA=' + str(Vars['Alpha']) + ' --Dec=' + str(Vars['Delta']) + ' --Freq=' + str(SearchBox[0]) + ' --f1dot=' + str(SearchBox[1]) + ' --f2dot=' + str(SearchBox[2]) + ' --FreqBand=' + str(SearchBand[0]) + ' --f1dotBand=' + str(SearchBand[1]) + ' --f2dotBand=' + str(SearchBand[2]) + ' --DataFiles="' + str(Vars['CFSInput']) + '/*.sft" --ephemEarth=' + str(Vars['EphemEarth']) + ' --ephemSun=' + str(Vars['EphemSun']) + ' --TwoFthreshold=' + str(Vars['2FThresh']) + ' --outputFstat=' + str(Vars['CFSOutput']) + ' --outputFstatHist=' + str(Vars['CFSHist']) + ' --metricMismatch=' + str(Vars['m']) + ' --gridType=8 --refTime=' + str(Vars['tStartGPS']) + ' --outputSingleFstats=TRUE --outputLoudest=' + str(Vars['CFSTopList']) + ' --useResamp=TRUE"'


							CFS.write('JOB ' + jobName + ' ' + CFSsubFileName + '\n')
							CFS.write('RETRY ' + jobName + ' 0\n')
							CFS.write(CFSv2Cmd + "\n\n")

							#StrainFactor Injection Frequency FrequencyBin SearchPos Alpha Delta	

							RecordCmd = str(strainfactor) + ' ' + str(i) + ' ' + str(Freq) + ' ' + str(search_record[searchindex,0]) + ' ' + str(Vars['SearchNo']) + ' ' + str(Vars['Alpha']) + ' ' + str(Vars['Delta'])

							record.write(RecordCmd + "\n")
						
if __name__ == "__main__":
	main(sys.argv[1:])

