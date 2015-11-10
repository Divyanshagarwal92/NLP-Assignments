#! /usr/bin/python
import re
import sys
import math

def emissionParameters(countFile):
	try:
		f = open( countFile, "r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read countfile %s.\n" %countFile )
		sys.exit(1)
	tmp = open('emissionParameters', 'w')
	lines = f.read()
	lines = lines.split('\n')
	emissionDic = {}
	tagDic = {}
	for line in lines:
		tokens = line.split()
		if( tokens[1] != 'WORDTAG'):
			break;
		counts = int(tokens[0])
		tag = tokens[2]
		word = tokens[3]
		#['6', 'WORDTAG', 'O', 'mind']
		tup = ( tag, word)
		if tup in emissionDic:
			emissionDic[tup] += counts
		else:
			emissionDic[tup] = counts
		if tag in tagDic:
			tagDic[tag] += counts
		else:
			tagDic[tag] = counts
	
	emissionParams = {}
	for key in emissionDic.keys():
		tag = key[0]
		emissionParams[key] = float(emissionDic[key]) / tagDic[tag]
		print key
		print emissionParams[key]
		print '\n'
	print '\n\n'
	tmp.close()
	return emissionParams

def getEmissionParams( word,  emissionParams ):
	taglist = ['I-ORG','B-ORG','I-PER','B-PER','I-LOC','B-LOC','I-MISC','B-MISC','O']
	#check if word is a rare word
		
	maxscore = 0.0000001
	flag = 0
	argtag = 'O'
	for tag in taglist:
		tup = (tag, word)
		if tup in emissionParams.keys():
			flag = 1
			if emissionParams[tup] > maxscore:
				maxscore = emissionParams[tup]
				argtag = tup[0]
	if flag == 0:
		for tag in taglist:
			tup = ( tag, '_RARE_')
			if tup in emissionParams:
				if emissionParams[tup] >= maxscore:
					maxscore = emissionParams[tup]
					argtag = tup[0]
	#print argtag + " " + str(maxscore)
	return [argtag, maxscore]

def simpleTagger( emissionParams, testFile):
	try:
		inputfile = open( testFile, "r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read file %s.\n" %rareFile )
		sys.exit(1)
			
	print 'Tagging... o/p file is prediction'
	outputfile = open( 'prediction', 'w')
	lines = inputfile.read()
	lines = lines.split('\n')

	taglist = ['I-ORG','B-ORG','I-PER','B-PER','I-LOC','B-LOC','I-MISC','B-MISC','O']
	for word in lines:
		if word == '':
			outputfile.write('\n')
			continue
		tmp = word 
		[argtag, maxscore] = getEmissionParams( word, emissionParams)
		sentence = tmp + " " + argtag + " " + str(math.log(maxscore))
		outputfile.write(sentence)
		outputfile.write('\n')

if __name__ == "__main__":
	if len(sys.argv) != 3:  
		print 'Usage: python ques4.py <countfile> <test.dat>'
		sys.exit(2)
	countFile = sys.argv[1]
	testFile = sys.argv[2]

	emissionParams = emissionParameters( countFile )
	simpleTagger( emissionParams, testFile)
