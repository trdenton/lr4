#!/bin/bash
while true; do
	./lr4.py 2>&1 | tee /tmp/lr4.log
done
