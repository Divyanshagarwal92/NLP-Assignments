#! /usr/bin/python
from sets import Set

import sys
import pickle
import math

def initialization( filename):
	print 'Initialization'
	output = open(filename, 'rb')
	t = pickle.load(output)
	output.close()
	return t


def calculateScore( gline, eline, tParams, qParams):

	engwords = eline.split(' ')
	gerwords = gline.split(' ')
	l = len(engwords)
	m = len(gerwords)

	engwords = ['NULL'] + engwords
	p = 1.0

	for i in range(m):
		gword = gerwords[i]
		alignScore = -1
		
		for j in range(l+1):
			eword = engwords[j]
			score = tParams.get( ( gword, eword), 0)\
					* qParams.get((j,i+1,l,m),0)
			if score > alignScore:
				alignScore = score
		if( alignScore!= 0 ):
			p = p + math.log( alignScore)
		else:
			p = p - 10000
	return p

def unscramble( engFile, germanFile, tParams, qParams):
	german = open( germanFile,'r')
	english = open( engFile,'r')
	germanCorpus = german.read()
	englishCorpus = english.read()
	germanLines = germanCorpus.split('\n')
	englishLines = englishCorpus.split('\n')

	outfile = open('unscrambled.en', 'w')

	for gline in germanLines:
		maxP = -1000000000
		maxSent = ''

		for e in range(len(englishLines)):
			eline = englishLines[e]
			P = calculateScore(gline, eline, tParams, qParams)

			if P > maxP:
				maxP = P
				maxSent = eline
		
		outfile.write(maxSent)
		outfile.write('\n')
	outfile.close()
	german.close()
	english.close()

def main():
	if(len(sys.argv) !=  3):
		print "Insufficient arguments"
		print "Sample command:"
		print 'python ques6.py scrambled.en original.de'
		return
	engFile = sys.argv[1]
	germanFile = sys.argv[2]
	
	
	tParams = initialization('transmission_Parameters_IBM2')
	qParams = initialization('alignment_Parameters_IBM2')
	
	
	unscramble( engFile, germanFile, tParams, qParams)

if __name__ == "__main__":
	main()

