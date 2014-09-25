#!/usr/bin/python

loudest2F = []

freq0 = 200.0

for step in xrange(0, 100):

	startfreq = freq0 + step*0.1
	
	if startfreq == int(startfreq):
		startfreq = int(startfreq)
	
	filename = "GammaSearch_" + str(startfreq) + "_1.dat"	
	filepattern = "Data/GS_880_" + str(startfreq) + "/*.sft"

	with open(filename) as f:
		data = f.readlines()[20:-1]

	Fstatlist = []

	for line in data:
		line = line.strip()
		columns = line.split()
		source = {}
		source['freq'] = columns[0]
		source['ra'] = columns[1]
		source['dec'] = columns[2]
		source['Fstat'] = columns[6]
		source['F0'] = str(startfreq)
		Fstatlist.append(source)

	loudest2F.append(Fstatlist[0])

	outputfilename = "UL_" + str(startfreq) + "_band"


	if step == 0:
		f = open('UL_GS_880_200.dag', 'wb')
	else: 
		f = open('UL_GS_880_200.dag', 'a+')

	f.write("JOB " + outputfilename + " AnalyticUL.sub\n")
	f.write("RETRY " + outputfilename + " 0\n")
	f.write("VARS " + outputfilename + ' argList=" -a ' + loudest2F[step]['ra'] + " -d " + loudest2F[step]['dec'] + " -f " + loudest2F[step]['F0'] + " -b 0.1 -F " + loudest2F[step]['Fstat'] + " -D '" + filepattern + "' -E /home/sano/master/opt/lscsoft/lalpulsar/share/lalpulsar -y 09-11 -o "+ outputfilename + '.txt"\n')
	f.write("\n")

	f.close()
