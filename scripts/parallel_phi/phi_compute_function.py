
import os
import sys
sys.path.append('../functions/')
import psutil
import numpy as np
import scipy.io as sio
import pyphi
import math
import itertools
import phi_functions

#https://pyphi.readthedocs.io/en/stable/configuration.html?highlight=after_computing_sia#pyphi.conf.PyphiConfig.CLEAR_SUBSYSTEM_CACHES_AFTER_COMPUTING_SIA
#pyphi.config.MAXIMUM_CACHE_MEMORY_PERCENTAGE = 50
# pyphi.config.CACHE_SIAS = False
# pyphi.config.CACHE_REPERTOIRES = False
# pyphi.config.CACHE_POTENTIAL_PURVIEWS = False
# pyphi.config.CLEAR_SUBSYSTEM_CACHES_AFTER_COMPUTING_SIA = False
pyphi.config.PROGRESS_BARS = False

# LEAVE AS FALSE - setting as true gives big slow down on MASSIVE
pyphi.config.PARALLEL_CUT_EVALUATION = False


def phi_compute(data, channel_set, channels, tau, source_suffix):

	# Results directory and filename
	results_dir = 'results/' + str(math.floor(channel_set / 1000000)) + '/' # Max files per directory = 1 million
	results_file = "{0:0>8}".format(channel_set) + source_suffix[:len(source_suffix)-4] + '_phi3.mat' # -4 refers to length of file extension, '.mat'

	# Get relevant data ##################################################################################

	channel_indices = [x - 1 for x in channels]
	channel_data = data[channel_indices, :]

	# Build TPM and network ############################################################################

	# Function takes format (samples x channels)
	tpm, state_counters = phi_functions.build_tpm_sbn(np.transpose(channel_data, axes=[1, 0]), tau, 2) # 2 - because data is binarised

	# Build the network and subsystem
	# We are assuming full connection
	network = pyphi.Network(tpm)
	print("Network built", flush=True)

	#########################################################################################
	# Remember that the data is in the form a matrix
	# Matrix dimensions: sample(2250) x channel(15)

	# Determine number of system states
	n_states = tpm.shape[0]
	nChannels = int(math.log(n_states, 2)) # Assumes binary values

	# Results structure
	phi = dict()

	# Initialise results storage structures
	state_sias = np.empty((n_states), dtype=object)
	state_phis = np.zeros((n_states))

	# sys.exit()

	# Calculate all possible phi values (number of phi values is limited by the number of possible states)
	for state_index in range(0, n_states):
		#print('State ' + str(state_index))
		# Figure out the state
		state = pyphi.convert.le_index2state(state_index, nChannels)
		
		# As the network is already limited to the channel set, the subsystem would have the same nodes as the full network
		subsystem = pyphi.Subsystem(network, state)
		
		#sys.exit()
		
		# Compute phi values for all partitions
		sia = pyphi.compute.sia(subsystem)
		
		#sys.exit()
		
		# Store phi and associated MIP
		state_phis[state_index] = sia.phi
		
		# MATLAB friendly storage format (python saves json as nested dict)
		# Store big_mip
		#state_sias[state_index] = pyphi.jsonify.jsonify(sia)
		
		print('State ' + str(state_index) + ' Phi=' + str(sia.phi), flush=True)

	# Store only phi values for each state
	#phi['sias'] = state_sias
	phi['state_phis'] = state_phis
	phi['tpm'] = tpm
	phi['state_counters'] = state_counters

	# Save ###########################################################################

	sio.savemat(results_dir + results_file, {'phi': phi}, do_compression=True, long_field_names=True)
	print('saved ' + results_dir + results_file, flush=True)
