#!/bin/bash

echo ""
echo "Running script for question 5 "

echo ""
echo "Learn suffix_tagger.model"
python ques5.py tag_train.dat suffix_tagger.model

echo ""
echo "Decode uing suffix_tagger.model"
python ques4.py suffix_tagger.model tag_dev.dat suffix_tag_dev.out


echo ""
echo "Output files created:"
echo "suffix_tagger.model"
echo "suffix_tag_dev.out"

echo ""
echo "Evaluation"
python eval_tagger.py tag_dev.key suffix_tag_dev.out
