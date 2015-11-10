#! /usr/bin/python
from sets import Set

import sys
import operator
import pickle
import simplejson

def buildVocabulary(Corpus):
	print 'Building Vocabulary'
	lines = Corpus.split('\n')
	vocab = set()
	for line in lines:
		words = line.split()
		vocab.update(words)
	#print vocab
	#print '\n\n\n'	
	return vocab

def initialization_t( filename):
	print 'Initialization t'
	output = open(filename, 'rb')
	t = pickle.load(output)
	return t

def initialization_q( germanCorpus, englishCorpus, germanVocab, englishVocab):
	print 'Initialization q'
	engLines = englishCorpus.split('\n')
	germanLines = germanCorpus.split('\n')

	q= {}
	numLines = len(engLines)
	
	for k in range(0,numLines):
		engWords = engLines[k].split(' ')
		germanWords = germanLines[k].split(' ')

		l = len(engWords)  #includes NULL word at 0th index
		m = len(germanWords)
		#engWords = ["NULL"] + engWords
		for i in range( 1, m+1):	#germanWords
			for j in range( 0, l+1):#engWords
				tup = ( j, i, l, m)
				q[tup] = 1.0/(l+1)
	return q 
def EM( numIters, germanCorpus, englishCorpus, englishVocab, tParams, qParams ):
	
	engLines = englishCorpus.split('\n')
	germanLines = germanCorpus.split('\n')
	countTup = {}
	count = {}

	countji = {}
	counti = {}

	for n in range( numIters):
		print 'Iteration #: ' + str(n)
		# set counts to 0
		for key in tParams:
			countTup[key] = 0
		for words in englishVocab:
			count[words] = 0
		for key in qParams:
			countji[key] = 0
			counti[key[1:]] = 0
		numlines = len(engLines)
		for k in range( numlines):
			englishWords = engLines[k].split(' ')
			germanWords = germanLines[k].split(' ')
			m = len(germanWords)
			l = len(englishWords)
			englishWords = ["NULL"] + engLines[k].split(' ')
			
			
			for i in range(m):
				gword = germanWords[i]
				denom = 0.0
				for j in range(l+1):
					eword = englishWords[j]
					denom = denom + tParams.get( (gword,eword),0)\
							* qParams.get( (j,i+1,l,m),0)
				if denom == 0:
					continue
				
				for j in range(l+1):
					#print eword, gword
					eword = englishWords[j]
					delta =  tParams.get((gword,eword),0)\
							* qParams.get( (j,i+1,l,m),0)\
							/ denom
					countTup[(gword,eword)] = countTup.get((gword,eword), 0) + delta
					count[eword] = count.get(eword,0) + delta
					counti[(i+1,l,m)] += delta 
					countji[j,i+1,l,m] += delta
		for key in countTup:
			eword = key[1]
			if eword not in count:
				continue
			tParams[key] = countTup.get( key, 0)/count[eword]
		for key in countji:
			tup = key[1:]
			if tup not in counti:
				continue
			qParams[key] = countji.get(key,0)/counti[tup]
	return [tParams, qParams]

def alignment(germanCorpus, englishCorpus, tParams, qParams):
	
	engLines = englishCorpus.split('\n')
	germanLines = germanCorpus.split('\n')
	outfile = open('alignment_outputfile_IBM2.txt', 'w')
	for s in range(20):
		indexList = []
		#print engLines[s]
		#print germanLines[s]
		engwords = engLines[s].split(' ')
		germanwords = germanLines[s].split(' ')
		l = len(engwords)
		m = len(germanwords)
		engwords = ['NULL'] + engwords 
		for i in range(m):
			gword = germanwords[i] 
			#print gword
			alignWord = ''
			alignScore = 0
			index = -1
			for j in range(l+1):
				eword = engwords[j]
				score = tParams[(gword,eword)]*qParams[(j,i+1,l,m)]
				if score > alignScore:
					alignScore = score 
					alignWord = eword
					index = j
			indexList.append(index)
			#print alignWord
		#print indexList
		#print '\n'
		outfile.write(engLines[s])
		outfile.write('\n')
		outfile.write(germanLines[s])
		outfile.write('\n')
		simplejson.dump( indexList, outfile)
		outfile.write('\n\n')
	outfile.close()


def main():
	if(len(sys.argv) !=  4):
		print "Insufficient arguments"
		print "Sample command:"
		print 'python ques5.py corpus.de corpus.en devwords.txt'
		return
	germanFile = sys.argv[1]
	engFile = sys.argv[2]
	german = open( germanFile,'r')
	english = open( engFile,'r')
	germanCorpus = german.read()
	englishCorpus = english.read()
	germanVocab = buildVocabulary(germanCorpus)
	englishVocab = buildVocabulary(englishCorpus)
	
	tParams = initialization_t('transmission_Parameters_IBM1')
	qParams = initialization_q( germanCorpus, englishCorpus, germanVocab, englishVocab)
	
	[ tParams, qParams] = EM( 5, germanCorpus, englishCorpus, englishVocab, tParams, qParams)
	
	output = open('transmission_Parameters_IBM2','w')
	pickle.dump( tParams, output)
	output.close()
	output = open('alignment_Parameters_IBM2','w')
	pickle.dump( qParams, output)
	output.close()

	alignment( germanCorpus, englishCorpus, tParams, qParams)

if __name__ == "__main__":
	main()

