#!/bin/bash

echo "Running script for question 4 "
python ques4.py tag.model tag_dev.dat tag_dev.out


echo ""
echo "Output files created:"
echo "tag_dev.out"

echo ""
echo "Evaluation"
python eval_tagger.py tag_dev.key tag_dev.out
