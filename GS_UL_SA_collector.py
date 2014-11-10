#/usr/bin/python

# GS_UL_SA_collector - collects results from upper limit validations.

from __future__ import division
import sys, getopt, array, ConfigParser, math
import numpy as np

def main(argv):
	
	usage = "GS_UL_SA_collector -f <frequency> -m <measured 2F> -l <lower directory> -u <upper directory> -s <lower strain> -b <upper strain> [-o <output file>]"

	try:
		opts, args = getopt.getopt(argv, "hf:m:l:u:s:b:o:", ["help", "measured2F=", "frequency=", "lowerDir=", "upperDir=", "lowerStrain=", "upperStrain=","outputFile="])
	except getopt.GetoptError:
		print usage
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print usage
			sys.exit()
		elif opt in ("-m", "--measured2F="):
			measured2F = float(arg)
		elif opt in ("-l", "--lowerDir"):
			lowerDir = arg
		elif opt in ("-u", "--upperDir"):
			upperDir = arg
		elif opt in ("-f", "--frequency"):
			freq = float(arg)
		elif opt in ("-s", "--lowerStrain"):
			hL = float(arg)
		elif opt in ("-b", "--upperStrain"):
			hU = float(arg)
		elif opt in ("-o", "--outputFile"):
			outputFile = arg

	#read in lower data
	
	lowerF = []
	l2Fex = []
	upperF = []
	u2Fex = []
	G = []
	N = []
	hprime = []

	for i in xrange(0,100):
		
		filename = "CFS_Out_Freq_" + str(freq) + "_Test_" + str(i) + ".dat"
	
		lowerLoc = lowerDir + "/" + filename
		
		with open(lowerLoc, 'r') as input:
			data = input.readlines()[20:21]

		for line in data:
			line = line.strip()
			columns = line.split()
			lF = float(columns[6])
			lowerF.append(lF)

		upperLoc = upperDir + "/" + filename

		with open(upperLoc, 'r') as input:
			data = input.readlines()[20:21]
		
		for line in data:
			line = line.strip()
			columns = line.split()
			uF = float(columns[6])
			upperF.append(uF)
		
		Gt = (uF - lF)/(hU**2-hL**2)
		Nt = (0.5*(uF + lF - (hU**2+hL**2)*Gt))

		l2Fex.append(Nt + Gt*hL**2)
		u2Fex.append(Nt + Gt*hU**2) 

		G.append(Gt)
		N.append(Nt)

		hprime.append(math.sqrt((measured2F-Nt)/Gt))

		
	lFconf = [j for j in l2Fex if j > measured2F]
	uFconf = [j for j in u2Fex if j > measured2F]

	print "lower strain confidence = " + str(len(lFconf)/100)
	print "upper strain confidence = " + str(len(uFconf)/100)
	print "G = " + str(np.mean(G)) 
	print "N = " + str(np.mean(N))

	hprime.sort(reverse=True)
	print hprime[0:6]

if __name__ == "__main__":
	main(sys.argv[1:])

