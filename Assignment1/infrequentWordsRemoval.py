#! /usr/bin/python
import re
import sys

def postProcessingInfrequentWords( trainFile, countFile ):
	try:
		f1 = open( trainFile, "r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read trainfile %s.\n" %trainFile)
		sys.exit(1)
	try:
		f2 = open( countFile, "r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read countfile %s.\n" %countFile )
		sys.exit(1)
	
	f = open('post_'+trainFile,'w')
	rarefile = open('rareFile','w')
	
	trainLines = f1.read();
	trainLines = trainLines.split('\n')
	rareWords = []
	
	lines = f2.read()
	lines = lines.split('\n')
	
	rareDic = {}	
	for line in lines:
		tokens = line.split(' ')
		if( tokens[1] != 'WORDTAG'):
			break;
		print tokens
		word  = tokens[3]
		count = int(tokens[0])
		if word in rareDic:
			print 'repeat'
			rareDic[word] = rareDic[word] + count
		else:
			rareDic[word] = count
	print len(rareDic)
	for key in rareDic:
		if rareDic[key] < 5:
			rareWords.append(key)
			rarefile.write(key)
			rarefile.write('\n')
	rarefile.close()
	print 'Creating post_ner.dat file'
	for line in trainLines:
		words = line.split(' ')
		if len(words)==0:
			continue
		for word in rareWords:
			if word == words[0]:
				words[0] = '_RARE_'
				break
		line = ' '.join(words)
		line = line + '\n'
		#print line,
		f.write(line)
	f.close()
	f1.close()
	f2.close()

if __name__ == "__main__":
	if len(sys.argv)!=3: # Expect exactly one argument: the training data file
		sys.exit(2)
	trainFile = sys.argv[1]
	countFile = sys.argv[2]
	postProcessingInfrequentWords(trainFile, countFile)

