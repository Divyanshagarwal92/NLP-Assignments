#!/usr/bin/python
import json
import sys

counts = {}

def modifyParseTree(tree):
	length = len(tree)
	if length == 2:
		if counts[tree[1]] < 5:
			print tree[1]
			#print counts[tree[1]]
			tree[1] = '_RARE_'
		return
	modifyParseTree(tree[1])
	modifyParseTree(tree[2])
	
def treeTraversal(tree):
	length = len(tree)

	if length == 2:
		word = tree[1]
		counts[word] = counts.get(word,0) + 1
		return
	
	treeTraversal(tree[1])
	treeTraversal(tree[2])

def main():
	if(len(sys.argv) !=  3):
		print "Insufficient arguments"
		print "Sample command:"
		print 'python q4.py parse_train.dat newfile.dat'
		return
	trainFilename = sys.argv[1]
	newFilename = sys.argv[2]
	newfile = open(newFilename,'w')
	trainfile = open(trainFilename,'r')

	# Read the file into lines
	lines = trainfile.read()
	lines = lines.split('\n')

	#Get word counts using training  parse trees
	for line in lines:
		if line == '':
			continue
		tree = json.loads(line)
		#update counts dictionary with the words of a given parse tree
		treeTraversal(tree)
	'''
	for key in counts:
		print key + " " + str(counts[key])
	'''
	#Modify parse trees for words having count < 5 
	for i in range(0,len(lines)):
		if lines[i] == '':
			continue
		tree = json.loads(lines[i])
		modifyParseTree(tree)
		newfile.write( unicode( json.dumps(tree, ensure_ascii=False)))
		newfile.write('\n')

if __name__ == "__main__":
	main()

