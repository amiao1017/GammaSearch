#!/usr/bin/python

import re

ULims = []

freq0 = 200.0

for step in xrange(0,1000):

	startfreq = freq0 + step*0.1

	if startfreq == int(startfreq):
		startfreq = int(startfreq)

	filename = "UL_" + str(startfreq) + "_band.txt"
	
	with open(filename) as f:
		data = f.readlines()[-3:-2]

	m = re.search('(?<=h0=)\d\.\d+e-\d+', data[0])

	band = {}
	band['freq'] = startfreq
	band['UL'] = float(m.group(0))
	
	if step == 0:
		f = open('UL_test_output_100.txt', 'wb')
	else: 
		f = open('UL_test_output_100.txt', 'a+')

	f.write(str(band['freq']) + " " + str(band['UL']) + "\n")
	f.close()

	ULims.append(band)
