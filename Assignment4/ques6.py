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

def get_suffix_features( features, word, tag_curr):
        suf1 = 'SUF1:' + word[-1:] + ':' + tag_curr
        suf2 = 'SUF2:' + word[-2:] + ':' + tag_curr
        suf3 = 'SUF3:' + word[-3:] + ':' + tag_curr
        features.append(suf1)
        features.append(suf2)
        features.append(suf3)
        return features 

def get_prefix_features( features, word, tag_curr):
	pre1 = 'PRE1:' + word[:1] + ':' + tag_curr
	pre2 = 'PRE2:' + word[:2] + ':' + tag_curr
	pre3 = 'PRE3:' + word[:3] + ':' + tag_curr
        features.append(pre1)
        features.append(pre2)
        features.append(pre3)
        return features 

def get_first_uppercase( features, word, tag_curr):
	if word[0].isupper():
		upper = 'UC1:' + tag_curr
		features.append(upper)
	return features
def get_number_features( features, word, tag_curr):
	if word.isdigit():
		number = 'NUM:' + tag_curr
		features.append(number)
	return features

def append_features( features, word, tag_curr, flag):
	if flag == 0:
		features = get_suffix_features( features, word, tag_curr)
		features = get_prefix_features( features, word, tag_curr)
		features = get_number_features( features, word, tag_curr)
		features = get_first_uppercase( features, word, tag_curr)
	elif flag == 1:
		features = get_suffix_features( features, word, tag_curr)
	elif flag == 2:
		features = get_number_features( features, word, tag_curr)
	elif flag == 3:
		features = get_first_uppercase( features, word, tag_curr)
	elif flag == 4:
		features = get_prefix_features( features, word, tag_curr)
	else:
		features = get_suffix_features( features, word, tag_curr)
		features = get_prefix_features( features, word, tag_curr)

	return features

	
def get_features( histories, sentence, flag):
	#histories is a list of history containing [index prev_tag curr_tag]
        words = sentence.split('\n')
	global_features = {}
        for history in histories:
                if history == '':
			continue
		#print history
		tokens = history.split()
                #print tokens
		if tokens[2] == 'STOP': 
                        continue
                #9  NOUN  VERB
                word_index = int(tokens[0]) - 1 
                tag_prev = tokens[1]
                tag_curr = tokens[2]
                word = words[word_index].split()[0]
		
		bigram = 'BIGRAM:' + tag_prev + ':' + tag_curr
		tag = 'TAG:' + word + ':' + tag_curr
                
		features = [bigram, tag]
		features = append_features( features, word, tag_curr, flag)
		for feature in features:
			global_features[feature] = global_features.get( feature, 0) + 1
	return global_features
def get_score( histories, sentence, model ,flag):
	result = ""	
        words = sentence.split('\n')
        for history in histories:
                tokens = history.split()
                if history == '' or tokens[2] == 'STOP': 
                        continue
                #9  NOUN  VERB
		#print tokens
                word_index = int(tokens[0]) - 1 
                tag_prev = tokens[1]
                tag_curr = tokens[2]
                word = words[word_index].split()[0]
		
		bigram = 'BIGRAM:' + tag_prev + ':' + tag_curr
		tag = 'TAG:' + word + ':' + tag_curr
		features = [ bigram, tag]
		features = append_features( features, word, tag_curr, flag)
		score = 0
                for feature in features:
                        score += model.get(feature,0)

                result += (history + ' ' + str(score) + '\n')
	return result[:-1]



def perceptron( train_file, model_file, gold_info, flag):
	gold_histories = gold_info[0]
	gold_features = gold_info[1]
	#print gold_features


	iteration = 5
	model = {}

	for t in range( 0, iteration):
		line_index = 0
		train_set = open( train_file, 'r')
		sentence = ''
		for line in train_set:
			if len(line) > 1:
				sentence += line
				continue

			sentence = sentence[:-1]
			histories = call(enumerate_server, sentence).split('\n')
			scores = get_score( histories, sentence, model, flag)
			#get the best matching history in tags
			best_history = call(history_server, scores)
			
			'''	
			print 'SCORES'
			print scores
			print '\n'
			print 'HISTORIES'
			print histories
			print '\n'
			print best_history
			print gold_histories[line_index]
			'''

			best_feature = get_features( best_history.split('\n'), sentence, flag)
			gold_feature = gold_features[line_index]
			'''
			print 'FEATURES'
			print gold_feature
			print best_feature
			print
			'''
			for feature in  gold_feature:
				model[feature] = model.get(feature,0) + gold_feature[feature]

			for feature in best_feature:
				model[feature] = model.get(feature, 0) - best_feature[feature]
			sentence = ''
			line_index += 1
		
		train_set.close()
	out = open(model_file, 'w')
	for feature in model:
		out.write(feature +  ' ' + str(model[feature]) + '\n')
	out.close()
	return model

def create_model( train_file, flag ):

	train_set = open(train_file,'r')
	sentence = ''
	gold_histories = {}
	gold_features = {}
	line_index = 0
	for line in train_set:
		if len(line) > 1:  
			sentence += line
			continue
		#gold_history is a string having new line charectars
		sentence = sentence[:-1]
		
		gold_history = call( gold_server, sentence)
		gold_histories[line_index] = gold_history
		gold_features[line_index] = get_features( gold_history.split('\n'), sentence, flag)
		
		#print gold_histories[line_index] 
		#print gold_features[line_index]
		sentence = ''
		line_index = line_index + 1 
	train_set.close()
	return [ gold_histories, gold_features]

def main():
	
	if len(sys.argv) != 4:
		print "Insufficient Arguments"
		print "Usage"
		print "python ques6.py tag_train.dat <model_name> <feature_flag - default 0>"
		return
	flag = int(sys.argv[3])
	gold_info = create_model( sys.argv[1], flag)
	
	model = perceptron( sys.argv[1], sys.argv[2], gold_info, flag)

if __name__ == "__main__":

	# default value of flag = 0
	'''
		flag = 0: Consider all
		flag = 1: Consider only suffix features
		flag = 2: Consider only number features
		flag = 3: Consider only first Capital letter features.
		flag = 4: Consider only prefix features
		flag = 5: Consider prefix and suffix features
	'''
	flag = 0
        enumerate_server = process(["python", "tagger_history_generator.py",  "ENUM"])
        gold_server = process(["python", "tagger_history_generator.py",  "GOLD"])

	history_server = process(['python', 'tagger_decoder.py', 'HISTORY'])
	main()

