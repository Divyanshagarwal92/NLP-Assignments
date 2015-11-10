#! /usr/bin/python
from subprocess import PIPE
import sys, subprocess

def process(args):
	"Create a 'server' to send commands to."
	return subprocess.Popen(args, stdin=PIPE, stdout=PIPE)

def call(process, stdin):
	"Send command to a server and get stdout."
	output = process.stdin.write(stdin + "\n\n")
	line = ""
	while 1:  
		l = process.stdout.readline()
		if not l.strip(): break
		line += l
	return line


#Read tag.model
#Initialize weights to parameter vector V - dictV
def read_model( model_file):
	model = open( model_file, 'r')
	lines = model.read()
	lines = lines.split('\n')
	dictV = {}
	for line in lines:
		if line == '':
			continue
		tokens = line.split(' ')
		key = tokens[0]
		param_score = float(tokens[1])
		dictV[key] = param_score

	#Testing dictV for correctness
	'''
	for key in dictV:
		print key,
		print ' ' + str(dictV[key])
	'''
	return dictV
def decoder( development_file, output_file,  model):
	
	development_set = open(development_file, 'r')
	output = open(output_file, 'w')
	
	sentence = ''
	for line in development_set:
		if len(line) > 1: 
			sentence += line
			continue
		
		#created a sentence
		sentence = sentence[:-1]
		#call enumerate server for GEN(x) set.
		histories = call(enumerate_server, sentence).split('\n')
		#get feature scores for the histories
		scores = get_score( histories, sentence, model)
		#get the best matching history in tags
		tags = call(history_server, scores).split('\n')
		words = sentence.split()
		#print words
		for i in range( 0, len(words) ):
			tag = tags[i].split()
			output.write(words[i] + ' ' + tag[2] + '\n')
		output.write('\n')
		#print tags	
		sentence = ''
def get_score(histories, sentence, model):
	result = ''
	words = sentence.split()
	for history in histories:
		if history == '':
			continue
		tokens = history.split()
		#print tokens
		#9  NOUN  VERB
		word_index = int(tokens[0]) - 1
		tag_prev = tokens[1]
		tag_curr = tokens[2]
		word = words[word_index]
		#print str(word_index) + " " + tag_prev + " " + tag_curr + " " + word
		features = get_features( word, tag_prev, tag_curr)
		
		score = 0
		for feature in features:
			score += model.get(feature,0)
		
		result += (history + ' ' + str(score) + '\n')
		#print features,
		#print  ' ' + str(score)
	#print result
	return result[:-1]

def get_features( word, tag_prev, tag_curr):
	bigram = 'BIGRAM:' + tag_prev + ':' + tag_curr
	tag = 'TAG:' + word + ':' + tag_curr
	features = [bigram, tag]
	features = get_suffix_features( features, word, tag_curr)
	return features 

def get_suffix_features( features, word, tag_curr):
	suf1 = 'SUF1:' + word[-1:] + ':' + tag_curr
	suf2 = 'SUF2:' + word[-2:] + ':' + tag_curr
	suf3 = 'SUF3:' + word[-3:] + ':' + tag_curr
	features.append(suf1)
	features.append(suf2)
	features.append(suf3)
	return features	
def main():
	if len(sys.argv) !=  4: 
		print "Insufficient arguments"
		print "Sample command:"
		print 'python ques4.py tag.model tag_dev.dat tag_dev.out'
		return
	model_file = sys.argv[1]
	development_file = sys.argv[2]
	output_file = sys.argv[3]
	model = read_model(model_file)
	decoder( development_file, output_file, model)
	


if __name__ == "__main__":
	enumerate_server = process(["python", "tagger_history_generator.py",  "ENUM"])
	history_server = subprocess.Popen(['python', 'tagger_decoder.py', 'HISTORY'], stdin=PIPE, stdout=PIPE)
	main()

