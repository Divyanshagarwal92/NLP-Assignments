#! /usr/bin/python

import re
import sys
import math

# Computes emission estimates
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
        # calcualting counts for ( tag, word)
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
        # calcualting emisssion params for (tag, word)
        for key in emissionDic.keys():
                tag = key[0]
                emissionParams[key] = float(emissionDic[key]) / tagDic[tag]
                '''
		print key
                print emissionParams[key]
                print '\n'
		'''
        print '\n\n'
        tmp.close()
        return emissionParams

# Computes trigram estimates
def computeParameters( countfile):
	try:
		f = open( countfile, 'r')
	except IOError:
		sys.stderr.write( "ERROR: Cannot read countfile %s.\n" %countFile )
		sys.exit(1)
	lines = f.read()
	lines = lines.split('\n')
	trigramDic = {}
	bigramDic = {}
	#3138 2-GRAM I-MISC O

	#calcualting trigram and bigram counts
	for line in lines:
		tokens = line.split()
		if len(tokens) == 0:
			continue

		counts = int(tokens[0])
		if tokens[1] == 'WORDTAG':
			continue
		if tokens[1] == '2-GRAM':
			tup = ( tokens[2], tokens[3])
			bigramDic[tup] = counts
		if tokens[1] == '3-GRAM':
			tup = ( tokens[2], tokens[3], tokens[4])
			trigramDic[tup] = counts
	
	#calcualting trigram estimates
	for key in trigramDic.keys():
		bigramKey = (key[0], key[1])
		trigramDic[key] = float(trigramDic[key])/bigramDic[bigramKey]
	for key in trigramDic.keys():
		print key
		print math.log(trigramDic[key])
	return trigramDic

# called by HMM_tagger to get the emission params, taking into account the words not seen in the corpus as well
def getEmissionParams( word, tag, emissionParams ):

        score = 0.0000001
	flag = 0
	tup = (tag, word)
	if tup in emissionParams.keys():
		flag = 1
		return emissionParams[tup]
        if flag == 0:
		tup = (tag, '_RARE_')
                if tup in emissionParams:
                	return emissionParams[tup]
	return score


# takes a list of words in a sentence and returns the list of tagged sequence
def HMM_tagger( words, trigramDic, emissionParams, taglist):
	

	pi = {}
	bp = {}
	numWords = len(words)
	if numWords == 0:
		return
	K = [];
	K.append('*')
	K.append('*')
	for i in range(0,numWords):
		K.append(taglist)
	
	# getEmissionParams( word, rareWords, emissionParams ):
	pi['0**'] = 1
	for k in range(2,numWords+2):
		for v in K[k-1]:
			for w in K[k]:
				maxScore = 0
				maxU = 'O'
				for u in K[k-2]:
					e1 = trigramDic[(u,v,w)] if (u,v,w) in trigramDic else 0
					e2 = getEmissionParams( words[k-2], w, emissionParams) 
					score = pi[str(k-2)+u+v] * e1 * e2
					if score > maxScore:
						maxScore = score
						maxU = u
				pi[str(k-1)+v+w] = maxScore
				bp[str(k-1)+v+w] = maxU
	maxU = 'O'
	maxV = 'O'
	maxScore = 0
	for u in K[numWords]:
		for v in K[numWords+1]:
			e1 = trigramDic[(u,v,'STOP')] if (u,v,'STOP') in trigramDic else 0
			score = pi[str(numWords)+u+v]* e1
			if score > maxScore:
				maxScore = score
				maxU = u
				maxV = v
	sentenceTags = [ maxU, maxV]
	for k in range( 0, numWords-2):
		sentenceTags.insert(0, bp[str(numWords-k)+sentenceTags[0]+sentenceTags[1]])
		#print pi[str(numWords-k)+sentenceTags[0]+sentenceTags[1]]
	return sentenceTags

def HMM_taggerWrapper( testFile, trigramDic, emissionParams, taglist):
        try:
                f = open( testFile, "r")
        except IOError:
                sys.stderr.write("ERROR: Cannot read countfile %s.\n" %countFile )
                sys.exit(1)
	
	output = open('prediction.viterbi','w')

	lines = f.read()
	lines = lines.split('\n')
	sentence = []
	for line in lines:
		if line == '':
			#print sentence
			sentenceTags = HMM_tagger( sentence, trigramDic, emissionParams, taglist)
			print sentenceTags
			for ind in range(0, len(sentence)):
				output.write( sentence[ind] + ' ' + sentenceTags[ind] )
				output.write('\n')
			output.write('\n')
			sentence = []
		else:
			sentence.append(line)
	output.close()
	f.close()
if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "Insufficient args"
		print "Usage: python ques5.py <countfile> <testFile> > <trigramEstimatesFile>"
		sys.exit(2)
	
	emissionParams = emissionParameters( sys.argv[1]) 
	
	trigramDic = computeParameters( sys.argv[1])
	
	taglist = ['B-ORG','I-ORG','I-PER','B-PER','I-LOC','B-LOC','I-MISC','B-MISC','O']
	
	#print 'Tagging....'
	HMM_taggerWrapper( sys.argv[2], trigramDic, emissionParams, taglist)
