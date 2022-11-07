#!bin/bash

NUM=1000
for i in $(seq 500 $NUM)
do
	STRING="https://www.gutenberg.org/cache/epub/${i}/pg${i}.txt"
	wget ${STRING}
done
