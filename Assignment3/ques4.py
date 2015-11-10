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

def initialization( germanCorpus, englishCorpus, germanVocab, englishVocab):
	print 'Initialization'
	engLines = englishCorpus.split('\n')
	germanLines = germanCorpus.split('\n')
	t = {}
	q= {}
	countGermanWords = {}
	for word in englishVocab:
		countGermanWords[word] = 0

	for i in range( len(engLines)):
		engWords = engLines[i].split(' ')
		germanWords = germanLines[i].split(' ')
		for indexE in range(0,len(engWords)):
			engWord = engWords[indexE]
			if engWord == '':
				continue
			countGermanWords[engWord] = countGermanWords[engWord] + len(germanWords)
			for indexG in range(0, len(germanWords)):
				germanWord = germanWords[indexG]
				tup = ( germanWord, engWord)
				t[tup] = 1
	for key in t:
		engWord = key[1]
		t[key] = 1.0/countGermanWords[engWord] 

	for germanWord in germanVocab:
		tup = (germanWord,'NULL')
		t[tup] = 1.0/len(germanVocab)
		#print tup, t[tup]
	return t

def EM( numIters, germanCorpus, englishCorpus, englishVocab, tParams ):
	
	engLines = englishCorpus.split('\n')
	germanLines = germanCorpus.split('\n')
	countTup = {}
	count = {}
	for i in range( 0, numIters):
		print 'Iteration #: ' + str(i)
		for key in tParams:
			countTup[key] = 0
		for words in englishVocab:
			count[words] = 0
		# set counts to 0

		for k in range( 0, len(engLines)):
			englishWords = ['NULL']
			englishWords = englishWords + engLines[k].split(' ')
			germanWords = germanLines[k].split(' ')
			for gword in germanWords:
				denom = 0.0
				for eword in englishWords:
					denom = denom + tParams.get( (gword,eword),0)
				if denom == 0:
					continue
				
				for eword in englishWords:
					#print eword, gword
					delta =  tParams.get((gword,eword),0)/denom
					countTup[(gword,eword)] = countTup.get((gword,eword), 0) + delta
					count[eword] = count.get(eword,0) + delta
		
		for key in countTup:
			eword = key[1]
			if eword not in count:
				continue

			tParams[key] = countTup.get( key, 0)/count[eword]
	return tParams

def estimation(filename, tParams, germanVocab):
	print 'Estimation\n\n'
	testfile = open(filename,'r')
	outfile = open('devwords_outputfile_IBM1.txt', 'w')
	lines = testfile.read()
	lines = lines.split('\n');
	for word in lines:
		#print word
		topEstimates = []
		if word == '':
			continue
		dic = {}
		for gword in germanVocab:
			tup = ( gword, word)
			if tup in tParams:
				score = tParams[tup]
				dic[gword] = score
		sortedDic = sorted(dic.items(), key=operator.itemgetter(1), reverse=True)
		for i in range(0,10):
			#print sortedDic[i]
			topEstimates.append(sortedDic[i])
		#print topEstimates
		outfile.write(word)
		outfile.write('\n')
		simplejson.dump( topEstimates, outfile)
		outfile.write('\n\n')
	outfile.close()

def alignment(germanCorpus, englishCorpus, tParams):
	
	engLines = englishCorpus.split('\n')
	germanLines = germanCorpus.split('\n')
	outfile = open('alignment_outputfile_IBM1.txt', 'w')
	for k in range(0,20):
		indexList = []
		engwords = ['NULL']
		engwords = engwords + engLines[k].split(' ')
		germanwords = germanLines[k].split(' ')
		for gword in germanwords:
			#print gword
			alignWord = ''
			alignScore = 0
			index = -1
			for i in range(0,len(engwords)):
				eword = engwords[i]
				if tParams[(gword,eword)] > alignScore:
					alignScore = tParams[(gword,eword)]
					alignWord = eword
					index = i
			indexList.append(index)
		outfile.write(engLines[k])
		outfile.write('\n')
		outfile.write(germanLines[k])
		outfile.write('\n')
		simplejson.dump( indexList, outfile)
		outfile.write('\n\n')
	outfile.close()
def main():
	if(len(sys.argv) !=  4):
		print "Insufficient arguments"
		print "Sample command:"
		print 'python ques4.py corpus.de corpus.en devwords.txt'
		return
	germanFile = sys.argv[1]
	engFile = sys.argv[2]
	german = open( germanFile,'r')
	english = open( engFile,'r')
	germanCorpus = german.read()
	englishCorpus = english.read()
	germanVocab = buildVocabulary(germanCorpus)
	englishVocab = buildVocabulary(englishCorpus)
	
	tParams = initialization( germanCorpus, englishCorpus, germanVocab, englishVocab)
	tParams = EM( 5, germanCorpus, englishCorpus, englishVocab, tParams)
	
	output = open('transmission_Parameters_IBM1','w')
	pickle.dump( tParams, output)
	output.close()
	
	estimation(sys.argv[3], tParams, germanVocab)
	alignment( germanCorpus, englishCorpus, tParams)
	
	german.close()
	english.close()
	#print tParams
if __name__ == "__main__":
	main()

