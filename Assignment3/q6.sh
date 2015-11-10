#!/bin/bash

echo "Running script for question 6 ( Approx time 1 mins)"
echo ""

python ques6.py scrambled.en original.de 

echo ""
echo "Output files created:"
echo "unscrambled.en"

echo ""
echo "Evaluation of results:"
python eval_scramble.py unscrambled.en original.en
