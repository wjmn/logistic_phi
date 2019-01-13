#!/bin/bash

# Find total number of parameter lines (total number of jobs to be submitted across all arrays)
lines=$(wc -l < networks_3ch_missing) # Total number of jobs which need to be computed

line_increment=1

# Loop through parameter lines
for (( line=1; line<=$lines; line=$line+$line_increment )); do
	squeue -u wjm07 > job_list
	jobs=$(wc -l < job_list)
	echo "there are $jobs jobs"
	while [ $jobs -ge 495 ]; do # Job limit is 500, to leave n spare jobs for anything else, specify 500-n as the limit
		echo "too many jobs, sleeping"
		sleep 60s
		squeue -u wjm07 > job_list
		jobs=$(wc -l < job_list)
		echo "slept, now there are $jobs jobs"
	done
	
	echo "array submitting (from line $line)"
	sbatch --job-name="${line}" --output="logs/${line}.out" --error="logs/${line}.err" bash_loop_sbatch.bash $line $line_increment
	echo "submitted"
done
