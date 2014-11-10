#!/usr/bin/python

import os, sys, getopt, glob

def main(argv):
	
	usage = "PositionUncertaintyCollector -s <source number> -i <input directory>"

	#get options from command line

	try:
		opts, args = getopt.getopt(argv, "hs:i:", ["help", "sourceNumber=","inputDir="])
	except getopt.GetoptError:
		print usage
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print usage
			sys.exit()
		elif opt in ("-s", "--sourceNumber"):
			sourceNumber = arg
		elif opt in ("-i", "--inputDir"):
			inputDir = arg

	filetypes = ['pRA', 'mRA', 'pDE', 'mDE']

	freqs = [100,120,140,160,180,200,300,400,500,600,700,800,900,1000]

	cosis = ['0','1']

	for type in filetypes:
	
		for cosi in cosis:

			outputFile = "source_" + str(sourceNumber) + "_" + type + "_cosi_" + cosi + ".dat"

			with open(outputFile, "w") as f:	

				Fstat = []

				for step in xrange(0,101):
	
					Fstat.append(step)

					for freq in freqs:
			
						filename = inputDir + "/" + type + "_cosi_" + cosi + "_freq_" + str(freq) + "_" + str(step) + ".dat"
					
						with open(filename, 'r') as input:
							data = input.readlines()[20:21]

						for line in data:
							line = line.strip()
							columns = line.split()
							Fstat.append(float(columns[6]))

					Fstat2 = str(Fstat)
		
					Fstat2 = Fstat2[1:-1]

					f.write(str(Fstat2) + "\n")

 
if __name__ == "__main__":
	main(sys.argv[1:])
