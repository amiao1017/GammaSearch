#!/usr/bin/python

# GS_UL_injection_writer - writes injections/searches for verifying analytic upper limits!

from __future__ import division
import sys, getopt, re, os, math, random, subprocess, array, ConfigParser
import numpy as np

def main(argv):

# eight sets of 100 injections made: strength 0.8, 0.95, 0.9h, 0.95h, 1.05h, 1.10h, 1.15, 1.2.

	usage = "GS_UL_injection_writer -c <config file> -r <record file> -s <start frequency> -e <end frequency> [--subFiles <sub file location>]"

	nInjections = 100
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

	try:
		Vars['SFTlocation'] = config.get("InjVars","InputData")
	except:
		sys.stderr.write("Cannot read SFTlocation\n")
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
	MFDlocation = outputLocation + "/" + "MFD_" + str(startFreq) + "_" + str(endFreq)
	MFDlogs = MFDlocation + "/" + "Logs"

	if not(os.path.isdir(outputLocation)):
		os.makedirs(outputLocation)
	if not(os.path.isdir(MFDlocation)):
		os.makedirs(MFDlocation)
	if not(os.path.isdir(MFDlogs)):
		os.path.isdir(MFDlogs)


        CFSsubFileName = subFileLocation+"/GS_UL_Injection_CFS_"+str(sourceNumber)+"_"+str(startFreq)+".sub"
        MFDsubFileLocation = subFileLocation+"/GS_UL_Injection_MFD_"+str(sourceNumber)+"_"+str(startFreq)

	with open(CFSsubFileName,"w") as f:
		f.write("universe=vanilla\n")
		f.write("executable = /home/sano/master/opt/lscsoft/lalapps/bin/lalapps_ComputeFStatistic_v2\n")
		f.write("arguments = $(argList)\n")
		f.write("log = "+outputLocation+"/GS_log.txt\n")
		f.write("error = " + outputLocation+"/GS_error.txt\n")
		f.write("output = " + outputLocation+"/GS_output.txt\n")
		f.write("notification = never\n")
		f.write("queue 1\n")

	if not(os.path.isdir(MFDsubFileLocation)):
		os.makedirs(MFDsubFileLocation)

	freqRange = endFreq-startFreq
	freqSteps = int(round(freqRange/Vars['FBand']))

	searchSteps = int(round(freqRange/Vars['SearchBand']))

	freqList = np.zeros((freqSteps))

   	h0_test = (0.8, 0.85, 0.9, 0.95, 1.05, 1.10, 1.15, 1.2)
	#h0_test = (0.9,0.95)
	TauSecs = Vars['Tau']*365*86400
	

	with open(injectionDag, "w") as MFDdag:

		with open(searchDag, "w") as CFS: 

			with open(injectionRecord, "w") as record:

				record.write('StrainFactor Injection 2F Frequency FrequencyBin SearchPos Alpha Delta\n')

				for search in range(0, searchSteps):

					Freq0 = Vars['FMin'] + Vars['SearchBand']*search
			
					for strainfactor in h0_test:
				
						strain_output = outputLocation + "/strain_" + str(strainfactor)

						if not(os.path.isdir(strain_output)):
							os.makedirs(strain_output)
					
						for i in xrange(0,nInjections):
					
							#generate random nuisance parameters
							Vars['CosIota'] = random.uniform(-1,1)
							Vars['Psi'] = random.uniform(0,2*math.pi)
							Vars['Phi0'] = random.uniform(0,2*math.pi)

							#generate random frequency parameters
							
							Freq = Vars['FMin'] + Vars['SearchBand']*(search + random.uniform(0,1))
						
							bindiff = search_record[:,0]-Freq
							binlist = bindiff[bindiff<0]
							searchindex = len(binlist)-1		

							
										
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

							MFDlogdir = MFDlogs + "/" + str(strainfactor) + "/" + str(Freq0)
		
							if not(os.path.isdir(MFDlogdir)):
								os.makedirs(MFDlogdir)

							Vars['MFDFmin'] = SearchBox[0] - Vars['Padding']
							Vars['MFDFBand'] = SearchBand[0] + 2*Vars['Padding']
							Vars['MFDLogFile'] = MFDlogdir + "/MFD_" + str(i) + ".txt"
							

							jobName = "GS_UL_Injection_"+ str(Freq0) + "_" + str(strainfactor)+ "_" + str(i)
						
							freq = math.floor(Freq*10.0)/10.0
	
							freqDir = str(10*math.floor(Vars['FMin']/10.0))
						
							MFDdir = MFDlocation + "/" + str(strainfactor) + "/" + str(Freq0) + "/" + str(i)

							if not(os.path.isdir(MFDdir)):
								os.makedirs(MFDdir)


							MFDCmdH1 = 'VARS ' + jobName + '_H1 argList=" --outSFTbname=' + MFDdir + " --IFO=H1 --ephemDir=" + str(Vars['EphemPath']) + ' --ephemYear='+str(Vars['EphemYrs']) + " --fmin=" + str(Vars['MFDFmin']) + " --Band=" + str(Vars['MFDFBand']) + " --refTime=" + str(Vars['startTime']) + " --Alpha=" + str(Vars['Alpha']) + " --Delta=" + str(Vars['Delta']) + " --h0=" + str(Vars['h0Test']) + " --cosi=" + str(Vars['CosIota']) + " --psi=" + str(Vars['Psi']) + " --phi0=" + str(Vars['Phi0']) + " --Freq=" + str(FreqVars[0]) + " --f1dot=" + str(FreqVars[1]) + " --f2dot=" + str(FreqVars[2]) + " --logfile=" + str(Vars['MFDLogFile']) + " --noiseSFTs=" + str(Vars['SFTlocation']) + "/" + freqDir + "/" + str(freq) + "/*.sft\""
							MFDCmdL1 = 'VARS ' + jobName + '_L1 argList=" --outSFTbname=' + MFDdir + " --IFO=L1 --ephemDir=" + str(Vars['EphemPath']) + ' --ephemYear='+str(Vars['EphemYrs']) + " --fmin=" + str(Vars['MFDFmin']) + " --Band=" + str(Vars['MFDFBand']) + " --refTime=" + str(Vars['startTime']) + " --Alpha=" + str(Vars['Alpha']) + " --Delta=" + str(Vars['Delta']) + " --h0=" + str(Vars['h0Test']) + " --cosi=" + str(Vars['CosIota']) + " --psi=" + str(Vars['Psi']) + " --phi0=" + str(Vars['Phi0']) + " --Freq=" + str(FreqVars[0]) + " --f1dot=" + str(FreqVars[1]) + " --f2dot=" + str(FreqVars[2]) + " --logfile=" + str(Vars['MFDLogFile']) + " --noiseSFTs=" + str(Vars['SFTlocation']) + "/" + freqDir + "/" + str(freq) + "/*.sft\""							
							MFDsubFileName = MFDsubFileLocation + "/GS_" + str(sourceNumber) + "_" + str(freq) + "_strain_" + str(strainfactor) + "_" + str(i)

						   	with open(MFDsubFileName,"w") as f:
								f.write("universe=vanilla\n")
								f.write("executable = /home/sano/master/opt/lscsoft/lalapps/bin/lalapps_Makefakedata_v4\n")
								f.write("arguments = $(argList)\n")
								f.write("log = "+ Vars['MFDLogFile'] +"\n")
								f.write("error = " + outputLocation+"/GS_MFD_error.txt\n")
								f.write("output = " + outputLocation+"/GS_MFD_output.txt\n")
								f.write("notification = never\n")
								f.write("queue 1\n")
							 										
							MFDdag.write('JOB ' + jobName +"_H1 " + MFDsubFileName + '\n')
							MFDdag.write('RETRY ' + jobName +"_H1 0\n")
							MFDdag.write(MFDCmdH1+"\n\n")	

							MFDdag.write('JOB ' + jobName +"_L1 " + MFDsubFileName + '\n')
							MFDdag.write('RETRY ' + jobName +"_L1 0\n")
							MFDdag.write(MFDCmdL1+"\n\n")				
								
							Vars['CFSInput'] = MFDdir + "/.sft"	

							#generates CFS and writes out to CFS dag
	
							if not(os.path.isdir(strain_output + "/CFS")):
								os.makedirs(strain_output + "/CFS")
		
							if not(os.path.isdir(strain_output + "/Hist")):
								os.makedirs(strain_output + "/Hist")

							Vars['CFSOutput'] = strain_output + "CFS/CFS_Out_Freq_" + str(Freq0) + "_Test_"+str(i)+".dat"
							Vars['CFSHist'] = strain_output + "Hist/CFS_Hist_Freq_"+ str(Freq0) + "_Test_" + str(i)+".dat"
							
							CFS.write('JOB ' + jobName + ' ' + CFSsubFileName + '\n')
							CFS.write('RETRY ' + jobName + ' 0\n')
							CFS.write("VARS " + jobName + ' argList=" --Alpha=' + str(Vars['Alpha']) + ' --Delta=' + str(Vars['Delta']) + ' --Freq=' + str(SearchBox[0]) + ' --f1dot=' + str(SearchBox[1]) + ' --f2dot=' + str(SearchBox[2]) + ' --FreqBand=' + str(SearchBand[0]) + ' --f1dotBand=' + str(SearchBand[1]) + ' --f2dotBand=' + str(SearchBand[2]) + ' --DataFiles=' + str(Vars['CFSInput']) + '/*.sft --NumCandidatesToKeep=100 --gridType=8 --outputFstat=' + str(Vars['CFSOutput']) + ' --outputFstatHist=' + str(Vars['CFSHist']) + ' --outputLogfile=' + strain_output + '/CFSlog.txt --refTime=' + str(Vars['startTime']) + ' --minStartTime=' + str(Vars['startTime']) + ' --maxEndTime=' + str(Vars['endTime']) + ' --outputSingleFstats=TRUE --metricMismatch=' + str(Vars['m']) + ' --dFreq=1e-6 --useResamp=TRUE --ephemEarth='+ str(Vars['EphemEarth']) + ' --ephemSun='+str(Vars['EphemSun'])+'"\n\n')


							#StrainFactor Injection 2F Frequency FrequencyBin SearchPos Alpha Delta	

							RecordCmd = str(strainfactor) + ' ' + str(i) + ' ' + str(search_record[searchindex,6]) + ' ' +  str(Freq) + ' ' + str(search_record[searchindex,0]) + ' ' + str(Vars['SearchNo']) + ' ' + str(Vars['Alpha']) + ' ' + str(Vars['Delta'])

							record.write(RecordCmd + "\n")
						
if __name__ == "__main__":
	main(sys.argv[1:])

