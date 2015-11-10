#!/usr/bin/python
import sys
import json

from sets import Set
Nt = {}
Brule = {}
Urule = {}
Nonterminals = Set()
seenWords = {}
binaryRuleDic = {}

def getParameters( countFilename):
	countfile = open(countFilename, 'r')
	lines = countfile.read()
	lines = lines.split('\n')
	for line in lines:
		if line == '':
			continue
		words = line.split(' ')
		count = int(words[0])
		if words[1] == 'NONTERMINAL':
			Nt[words[2]] = Nt.get(words[2],0) + count
			Nonterminals.add(words[2])
		elif words[1] == 'BINARYRULE':
			tup = ( words[2], words[3], words[4])
			if words[2] in binaryRuleDic:
				binaryRuleDic[words[2]].append((words[3], words[4]))
			else:
				binaryRuleDic[words[2]] = [ ( words[3], words[4])]
			Brule[tup] = Brule.get( tup, 0) + count
		elif words[1] == 'UNARYRULE':
			tup = ( words[2], words[3])
			Urule[tup] = Urule.get( tup, 0) + count
			seenWords[words[3]] = seenWords.get(words[3], 0) + 1 
	for key in Urule:
		nonTerminal = key[0]
		Urule[key] = float(Urule[key])/ Nt[nonTerminal]
	
	for key in Brule:
		nonTerminal = key[0]
		Brule[key] = float(Brule[key])/Nt[nonTerminal]
		#print key
		#print Brule[key]
	#print 'Binary rules'
	count = 0
	for nonterminal in binaryRuleDic:
		count = count+1
		#print nonterminal
		#print binaryRuleDic[nonterminal]
		#print '\n'
	#print count
def CKYParser( sentence):

	pi = {}
	bp = {}
	n = len(sentence)
	#Intialization

	for i in range(0, n):
		for X in Nonterminals:
			tup = ( X, sentence[i])
			#print tup
			if tup in Urule.keys():
				#print 'Seen Word: Unary Rule exists'
				pi[str(i)+str(i)+X] = Urule[tup]
				#print tup
				#print pi[str(i)+str(i)+X]
			elif sentence[i] in seenWords.keys():
				#print 'Seen Word: Unary Rule does not exist'
				continue
			elif (X,'_RARE_') in Urule.keys():	
				#print 'Unseen or Rare Word: Unary Rule exist'
				pi[str(i)+str(i)+X] = Urule[(X,'_RARE_')]
			else:
				#print 'Unseen or Rare Word: Unary Rule does not exist'
				continue
			if pi[str(i)+str(i)+X] == 0:
				continue
				#print 'dafuq'
	#Algorithm
	
	for l in range(1,n):
		for i in range(0, n-l): 
			j = i + l
			#print str(i) + str(j)
			for X in Nonterminals:
				#print 'X: ' + X
				maxScore = 0
				maxargs = ''
				if X not in binaryRuleDic:
					continue
				for rule in binaryRuleDic[X]:
					Y = rule[0]
					Z = rule[1]
					for s in range( i, j):
						score = 0
						tup = (X,Y,Z)
						rule1 = str(i)+str(s)+Y
						rule2 = str(s+1)+str(j)+Z
						if tup not in Brule:
							continue
						if rule1 not in pi:
							continue
						if rule2 not in pi:
							continue
						score = Brule[(X,Y,Z)]*pi[rule1]*pi[rule2]
						args = (Y,Z,s)
						'''
						if X == 'S' and i == 0 and j == n-1 and score != 0 :
							print "final answer"
							print score
							print args
						'''
						if score > maxScore:
							maxScore = score
							maxargs = args
				if maxScore != 0:
					pi[str(i)+str(j)+X] = maxScore
					bp[str(i)+str(j)+X] = maxargs

	key = str(0)+str(n-1)+'S'
	key2 = [ 0, n-1, 'S']
	tree = []
	if key in pi:
		#print pi[str(0)+str(n-1)+'S']
		#print 'backpointer processing'
		tree = reccursive(bp, sentence,key2)
		#print tree
	else:

		score = 0
		arg = ''
		for X in Nonterminals:
			key = str(0)+str(n-1)+X
			if key in pi:
				if score < pi[key]:
					score = pi[key]
					arg = X
		key2 = [ 0, n-1, arg]
		#print 'backpointer processing'
		tree = reccursive( bp, sentence, key2)
		#print tree
	
	#print 'End Algorithm'
	#print '\n'
 	return tree
def reccursive( bp, sentence, key):
	left = key[0]
	right = key[1]
	X = key[2]
	if left==right:
		return [ X, sentence[left]]

	key2 = str(left)+str(right)+X
	(Y,Z,center) = bp[key2]

	leftChild = reccursive(bp,sentence,[ left, center, Y])
	rightChild = reccursive(bp,sentence,[ center+1, right, Z])
	return [X, leftChild, rightChild]
def CKYParserWrapper( parseFilename, predictionFilename):
	parsefile = open( parseFilename,'r')
	predictionfile = open( predictionFilename, 'w')
	lines = parsefile.read()
	lines = lines.split('\n')

	for i in range( 0, len(lines)):
		if lines[i] == '':
			continue
		#print lines[i]
		sentence = lines[i].split(' ')
		#print sentence
		tree = CKYParser(sentence)
		predictionfile.write( unicode( json.dumps(tree, ensure_ascii=False)))
		predictionfile.write('\n')

def main():
	if len(sys.argv) !=  4:
		print "Insufficient arguments"
		print "Sample command:"
		print 'python q5.py countsfile parse_dev.dat predictionfile'
		return

	countFilename = sys.argv[1]
	parseFilename = sys.argv[2]
	predictionFilename = sys.argv[3]
	getParameters( countFilename )
	CKYParserWrapper(parseFilename, predictionFilename)

if __name__ == '__main__':
	main()
