import pyphi as pyphi
import numpy as np

def build_tpm_sbn(data, tau, n_values):
	"""
	Builds a state-by-node TPM, holding the probabilities of each node being "on" given some past
	network states
	
	http://pyphi.readthedocs.io/en/stable/conventions.html?highlight=state%20by%20node
	
	Inputs:
		fly_data = matrix (of discretised data) with dimensions (samples x channels)
			Holds data across which TPM should be built
		tau = integer - the lag between current and future states
			e.g. 1 means that the current and future sample are adjacent
			e.g. 2 means that there is one sample between the current and future samples, etc.
		n_values = number of states each *node* can be in (e.g. 2 for ON and OFF)
	Outputs:
		tpm = matrix with dimensions (n_values^channels x channels)
			Each row holds the probabilities of each channel being "on" in the future, given a past
			network state
	"""
	
	import pyphi as pyphi
	import numpy as np
	
	# Determine number of system states
	n_states = n_values ** data.shape[1]
	
	# Declare TPM (all zeros)
	tpm = np.zeros((n_states, data.shape[1]))
	
	"""
	TPM Indexing (LOLI):
	e.g. for 4x4 TPM:
	
	0 = 00
	1 = 10
	2 = 01
	3 = 11
	
	Use pyphi.convert.state2loli_index(tuple) to get the index (v0.8.1)
	Use pyphi.convert.state2le_index(tuple) in v1
	"""
	
	# Declare transition counter (we will divide the sum of occurrences by this to get empirical probability)
	transition_counter = np.zeros((n_states, 1))
	
	for sample in range(0, data.shape[0]-tau): # The last sample to transition is the tauth last sample (second last if tau==1) (remember that the end of range() is exclusive)
		sample_current = data[sample, :]
		sample_future = data[sample+tau, :]
		
		# Identify current state
		state_current = pyphi.convert.state2le_index(tuple(sample_current))
		
		# Future boolean state
		sample_future_bool = sample_future.astype(bool)
		
		# Increment 'on' channels by 1
		tpm[state_current, sample_future_bool] += 1
		
		# Increment transition counter
		transition_counter[state_current] += 1
	
	state_counter = np.copy(transition_counter)
	
	# Divide elements in TPM by transition counter
	# If counter is 0, then transition never occurred - to avoid dividing 0 by 0, we set the counter to 1
	for state, counter in enumerate(transition_counter):
		if counter == 0:
			transition_counter[state] = 1
			tpm[state, :] = 1 / n_values # maximum entropy if no observations
	tpm /= transition_counter # This division works because of how we declared the vector ((n_states x 1) matrix)
	
	return tpm, state_counter