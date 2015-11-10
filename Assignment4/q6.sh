#!/bin/bash

echo ""
echo "Running script for question 6 "

echo ""
echo "Experiment - 1: Consider all additional features - prefix, suffix, numbers, capital"
python ques6.py tag_train.dat all_tagger.model 0
python ques4.py all_tagger.model tag_dev.dat all_tag_dev.out 
python eval_tagger.py tag_dev.key all_tag_dev.out 
echo ""

echo "Experiment - 2: Consider additional features -  suffix "
python ques6.py tag_train.dat suffix_tagger.model 1
python ques4.py suffix_tagger.model tag_dev.dat suffix_tag_dev.out 
python eval_tagger.py tag_dev.key suffix_tag_dev.out 
echo ""


echo "Experiment - 3: Consider additional features -  number"
python ques6.py tag_train.dat number_tagger.model 2
python ques4.py number_tagger.model tag_dev.dat number_tag_dev.out 
python eval_tagger.py tag_dev.key number_tag_dev.out 
echo ""

echo "Experiment - 4: Consider additional features -  capital"
python ques6.py tag_train.dat capital_tagger.model 3
python ques4.py capital_tagger.model tag_dev.dat capital_tag_dev.out 
python eval_tagger.py tag_dev.key capital_tag_dev.out 
echo ""

echo "Experiment - 5: Consider additional features -  prefix and suffix "
python ques6.py tag_train.dat pre-suf_tagger.model 5
python ques4.py pre-suf_tagger.model tag_dev.dat pre-suf_tag_dev.out 
python eval_tagger.py tag_dev.key pre-suf_tag_dev.out 
echo ""

echo "Experiment - 6: Consider additional features -  prefix"
python ques6.py tag_train.dat prefix_tagger.model 4
python ques4.py prefix_tagger.model tag_dev.dat prefix_tag_dev.out 
python eval_tagger.py tag_dev.key prefix_tag_dev.out 
echo ""


