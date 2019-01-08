import sys
import os
import subprocess
import pyphi
from phi_compute_function import *

# channel_sets should be specified in file 'networks_2ch', which holds channel_sets:
#	1,2
#	1,3
#	...
#	100,101
#	etc.


lines = sys.argv[1].split('\n')

tau = 1

# Setup ############################################################################

pyphi.config.LOG_FILE = 'logs_pyphi/' + lines[0].strip().split(',')[0] + '.log' # Log to file specific for this script

# Source directory and filename
source_dir = '../data/'
source_prefix = '003_SD3.00_20180513'
source_suffix = '_binAverage1_medianSplit.mat'

# Load data ############################################################################

print('loading data')

loaded = sio.loadmat(source_dir + source_prefix + source_suffix)
data = loaded['df_f_binarised']

print("loaded")

# # Make results directory if it doesn't exist
# # Results directory and filename
# first_network = int(lines[0].split(',')[0]) # First network
# result_dir = math.floor(first_network / 1000000) # Max 1 million files per directory
# extra_results = result_dir + 1 # Extra results directory, in case the loop crosses the million mark

# # Make directory if it doesn't exist
# os.makedirs(os.path.dirname('results/' + str(result_dir) + '/'), exist_ok=True)
# os.makedirs(os.path.dirname('results/' + str(extra_results) + '/'), exist_ok=True)

# Loop through
for line in range(len(lines)):
	
	params = list(map(int, lines[line].strip('\r#').split(','))) # each line has '\r,' last line has '\r#' (no '\n' because the original string was split on '\n')
	channel_set = params[0]
	channels = params[1:]
	
	print('computing - ' + str(channel_set) + ': ' + str(channels), flush=True)
	
	phi_compute(data, channel_set, channels, tau, source_suffix)

print('loop finished', flush=True)