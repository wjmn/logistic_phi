#!/bin/bash
# Usage: sbatch slurm-serial-job-script
# Prepared By: Kai Xi,  Oct 2014
#              help@massive.org.au

# NOTE: To activate a SLURM option, remove the whitespace between the '#' and 'SBATCH'

# $1: line counter
# Need to use variables OUTSIDE of this script, #SBATCH doesn't support variables: https://help.rc.ufl.edu/doc/Using_Variables_in_SLURM_Jobs
# SBATCH --job-name=f$1s$2c$3t$4t$5


# To set a project account for credit charging, 
#SBATCH --account=qb48


# Request CPU resource for a serial job
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
# SBATCH --exclusive
#SBATCH --cpus-per-task=1

# Memory usage (MB)
#SBATCH --mem-per-cpu=8000

# Set your minimum acceptable walltime, format: day-hours:minutes:seconds
#SBATCH --time=6-20:00:00

#SBATCH --qos=normal

# To receive an email when job completes or fails
# SBATCH --mail-user=jwu202@student.monash.edu
# SBATCH --mail-type=END
# SBATCH --mail-type=FAIL


# Set the file for output (stdout)
# SBATCH --output=logs/myJob-fly2-%j.out

# Set the file for error log (stderr)
# SBATCH --error=logs/$1_$2_$3.err


# Use reserved node to run job when a node reservation is made for you already
# SBATCH --reservation=reservation_name


# Job script

module load python/3.6.2

source ../../../pyphi_environment/bin/activate

# Extract relevant lines to separate file
lines=$(sed -n "${1},$((${1}+${2}-1))p;$((${1}+${2}))q" "networks_4ch_extra")# > networks/$1

# Run python loop script using small networks-file
time python3 -W ignore -m cProfile -s tottime phi_compute_loop.py "${lines}"
#time python -W ignore -m cProfile -s tottime phi_compute_loop.py 1 $2 networks/ $1

# Run python loop script
#python phi_compute_loop.py $1 $2

# Loop through assigned lines, run python script
# for (( line=${1}; line<=${1}+${2}-1; line=$line+1 )); do
	
	# # # Check if file already exists
	# # printf -v line_padded "%08d" $line
	# # out_file="results/${line_padded}_binAverage1_medianSplit_phi3.mat"
	
	# # if [ -f "${out_file}" ]; then
		# # # File already exists, don't recompute
		# # echo "${out_file} already exists"
	# # else
		# # echo "${out_file} doesn't exist, will try and compute"
		# # # Read params from file (file is networks_2ch)
		# # # $1 gives parameter line for the first job
		# # # $2 gives how many lines to do
		# # params=$(sed -n "$((${line}))p" "networks_2ch")
		
		# # if [[ -n "$params" ]]; then
			# # # If the parameters exist, compute
			# # python phi_compute.py $line $params
		# # fi
	# # fi
	
	# # Read params from file (file is networks_2ch)
	# # $1 gives parameter line for the first job
	# # $2 gives how many lines to do
	# params=$(sed -n "$((${line}))p" "networks_2ch")
	
	# if [[ -n "$params" ]]; then
		# # If the parameters exist, compute
		# python phi_compute.py $line $params
	# fi
	
# done

deactivate
