import os
import sys
sys.path.append('../parallel_phi/')
import psutil
import numpy as np
import scipy.io as sio
import pyphi
import math
import itertools
from phi_functions import *
from phi_tpm_log_reg import *

#https://pyphi.readthedocs.io/en/stable/configuration.html?highlight=after_computing_sia#pyphi.conf.PyphiConfig.CLEAR_SUBSYSTEM_CACHES_AFTER_COMPUTING_SIA
#pyphi.config.MAXIMUM_CACHE_MEMORY_PERCENTAGE = 50
# pyphi.config.CACHE_SIAS = False
# pyphi.config.CACHE_REPERTOIRES = False
# pyphi.config.CACHE_POTENTIAL_PURVIEWS = False
# pyphi.config.CLEAR_SUBSYSTEM_CACHES_AFTER_COMPUTING_SIA = False
pyphi.config.PROGRESS_BARS = False

# LEAVE AS FALSE - setting as true gives big slow down on MASSIVE
pyphi.config.PARALLEL_CUT_EVALUATION = False


def calculate_phis_all_methods(data, channel_set, channels):
    """ Calculate phi using all methods available.

    Args:
        data (np.ndarray): (samples, channels, trials, flies, conds) array of BINARISED data.
        channel_set (int): ID of channel set.
        channels (tuple of ints): Channels to be included in phi calculation (as indices of data).
                                  Channels should be 0-indexed (Python convention).
    
    Returns:
        Nothing. Instead, saves processed data as .mat files.
    """

    ("COMPUTING {}\n".format(channel_set))
    
    channels = tuple(channels)

    n_test_channels = len(channels)
    
    calculate_phis(data, n_test_channels, channels, "direct")
    
    calculate_phis(data, n_test_channels, channels, "logistic", interaction_order=0)
    
    for i_o in range(1, n_test_channels):
        calculate_phis(data, n_test_channels, channels, "logistic", interaction_order=i_o)
    

def calculate_phis(data, n_test_channels, ch_group, method, **kwargs):
    """ Calculates and saves phi values for a given number of test_channels for a given method.
    
    Args:
        data (np.ndarray): (samples, channels, trials, flies, conds) array of BINARISED data.
        n_test_channels (int): Number of channels to consider at a time. Minimum 2.
        method (string): Method used to generate TPM. 
                         Must be one of:
                         - "direct"
                         - "logistic" (requires kwarg interaction_order)
        ch_group (tuple of ints): Channels to be included in phi calculation.
    
    Keyword Args:
        interaction_order (int): Parameter used for logistic method for TPM calculation.
    
    Returns:
        Nothing. 
        Instead, saves lists of dictionaries (per channel group) as .mat files with keys:
            i_trial
            i_fly
            i_cond
            state_phis
            tpm
            state_counts
            channels
    
    """
    
    n_samples, n_channels, n_trials, n_flies, n_conds = data.shape
    
    tau = 1
    
    results_dir = "../../data/processed/phis/"
    
    ch_groups = itertools.combinations(range(n_channels), n_test_channels)
    
    if method == "direct":
        method_str = method
    elif method == "logistic":
        if "interaction_order" not in kwargs:
            raise ValueError("Must specify interaction_order if using logistic method.")
        interaction_order = kwargs.get("interaction_order")
        method_str = method + str(interaction_order)
    else:
        raise ValueError("Method specified was not recognised")
    
    # This deeply nested loop will take a long time...
    ch_group_results = []
    data_slice = data[:, ch_group, :, :, :]
    for cond in range(n_conds):
        #print("CONDITION {}".format(cond))
        for fly in range(n_flies):
            #print("  FLY {}".format(fly))
            for trial in range(n_trials):
                #print("    TRIAL {}".format(trial))
                if method == "direct":
                    tpm, state_counts = build_tpm_sbn(data_slice[:, :, trial, fly, cond], tau, 2)
                else:
                    tpm, state_counts = tpm_log_reg(data_slice[:, :, trial, fly, cond], tau, interaction_order)

                n_states = n_test_channels ** 2

                network = pyphi.Network(tpm)
                phi = dict()
                state_sias = np.empty((n_states), dtype=object)
                state_phis = np.zeros((n_states))
                for state_index in range(n_states):
                    state = pyphi.convert.le_index2state(state_index, n_test_channels)
                    subsystem = pyphi.Subsystem(network, state)
                    #sia = pyphi.compute.sia(subsystem)
                    phi_val = pyphi.compute.phi(subsystem)
                    state_phis[state_index] = phi_val
                    #print('      STATE {}, PHI = {}'.format(state, phi_val))

                # Store only phi values for each state
                #phi['sias'] = state_sias
                phi['state_phis'] = state_phis
                phi['tpm'] = tpm
                phi['state_counts'] = state_counts
                phi['i_trial'] = trial
                phi['i_fly'] = fly
                phi['i_cond'] = cond
                phi['channels'] = ch_group

                ch_group_results.append(phi)


    results_file = "PHI_{}_METHOD_{}_CHS_{}.mat".format(n_test_channels,
                                                        method_str,
                                                        "-".join(map(str, ch_group)))

    sio.savemat(results_dir + results_file, {'ch_group_results': ch_group_results}, do_compression=True, long_field_names=True)
    print('      SAVED {}\n'.format(results_dir + results_file))
