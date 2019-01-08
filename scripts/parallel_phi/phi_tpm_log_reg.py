import pyphi
import numpy as np
import itertools
import patsy
from sklearn.linear_model import LogisticRegression
def gen_log_reg(data, tau=1, interaction_order=0):
    """ Generate logistic regression for binarised past and present states.
    
    Args:
        data (array): (timepoints, channels, trials) array of binarised data.
                      The data will pool each timepoint step as a separate trial.
        tau (int): Time lag between present and next state.
        interaction_order (int): Order of interaction terms to be used.
                                 If 0, ALL interaction terms are included.
                                 If 1, NO interaction terms are included (i.e. all input order 1).
                                 If 2, interaction terms e.g. x1:x2 are included etc.
                      
    Returns: 
        List of Logistic regressions (fitted) for each channel.
    """
    
    n_timepoints, n_channels, n_trials = data.shape
    
    if interaction_order > n_channels:
        raise ValueError("Interaction order must not exceed number of channels.")
    
    presents = data[:n_timepoints - tau, :, :]\
                .transpose(2, 0, 1)\
                .reshape((n_trials * (n_timepoints - tau), n_channels))
    nexts = data[tau:, :, :]\
                .transpose(2, 0, 1)\
                .reshape((n_trials * (n_timepoints - tau), n_channels))
    
    # ----------------------------------------------------------------------------
    # FOR TESTING ONLY 
    # Once a "method" has been decided, the extraneous code can be removed.
    # ----------------------------------------------------------------------------
    
    x_vars = ["x{}".format(i_x) for i_x in range(n_channels)]
    
    if interaction_order == 0:
        data_dict = {"x{}".format(i_x): presents[:, i_x] for \
                    i_x in range(n_channels)}

        patsy_str = "*".join(x_vars)

        X_dmatrix = patsy.dmatrix(patsy_str, data_dict)
        Xs = X_dmatrix[:, 1:] # exclude intercept term
    elif interaction_order == 1:
        Xs = presents
    else:
        data_dict = {"x{}".format(i_x): presents[:, i_x] for \
            i_x in range(n_channels)}
        patsy_str = " + ".join(x_vars)
        for i_o in range(2, interaction_order + 1):
            combinations = itertools.combinations(x_vars, i_o)
            comb_strs = map(":".join, combinations)
            patsy_str += " + " + " + ".join(comb_strs)
            X_dmatrix = patsy.dmatrix(patsy_str, data_dict)
            Xs = X_dmatrix[:, 1:] # exclude intercept term
    
    # ----------------------------------------------------------------------------
    
    models = []
    
    for i_c in range(n_channels):
        y = nexts[:, i_c]
        lr = LogisticRegression(solver='lbfgs')
        model = lr.fit(Xs, y)
        models.append(model)
    
    return models
def models_to_tpm(models, n_channels, interaction_order=0):
    """ Converts a logistic regression model to a TPM
    
    Args:
        models: List of fitted logistic regression models.
        n_channels (int): Number of channels used to generate model.
        interaction_order (int): Order of interaction terms used to define model.
        
    Returns:
        A numpy array as a TPM.
    """
    
    tpm_shape = [2] * n_channels + [n_channels]
    
    tpm = np.zeros(tpm_shape)
    
    for state in itertools.product((0, 1), repeat=n_channels):
        for i_m, model in enumerate(models):
            state_arr = np.array(state)
            
            # ----------------------------------------------------------------------------
            # FOR TESTING ONLY 
            # Once a "method" has been decided, extraneous code can be removed.
            # ----------------------------------------------------------------------------
            x_vars = ["x{}".format(i_x) for i_x in range(n_channels)]
            
            if interaction_order == 0:
                data_dict = {"x{}".format(i_x): state_arr[i_x] for \
                            i_x in range(n_channels)}
                patsy_str = "*".join(x_vars)
                state_dmatrix = patsy.dmatrix(patsy_str, data_dict)
                state_all = state_dmatrix[:, 1:]
            elif interaction_order == 1:
                state_all = state_arr.reshape(1, -1)
            else:
                data_dict = {"x{}".format(i_x): state_arr[i_x] for \
                    i_x in range(n_channels)}
                patsy_str = " + ".join(x_vars)
                for i_o in range(2, interaction_order + 1):
                    combinations = itertools.combinations(x_vars, i_o)
                    comb_strs = map(":".join, combinations)
                    patsy_str += " + " + " + ".join(comb_strs)
                    state_dmatrix = patsy.dmatrix(patsy_str, data_dict)
                    state_all = state_dmatrix[:, 1:] # exclude intercept term
            tpm[state + (i_m,)] = model.predict_proba(state_all)[0][1]
            # ----------------------------------------------------------------------------
    
    return tpm
def tpm_log_reg(data, tau=1, interaction_order=0):
    """ Generate tpm using log regression for binarised past and present states.
    
    Args:
        data (array): (timepoints, channels, trials) array of binarised data.
                      The data will pool each timepoint step as a separate trial.
                      Will also accept (timepoints, channels) 2D array.
                      
    Returns: 
        TPM for the input data.
    """
    
    if len(data.shape) == 2:
        data = np.expand_dims(data, axis=-1) # adds trial axis, 1 "trial"
    
    n_timepoints, n_channels, n_trials = data.shape
    
    models = gen_log_reg(data, tau, interaction_order)
    
    tpm = models_to_tpm(models, n_channels, interaction_order)
    
    state_counter = np.zeros(2 ** n_channels)
    
    pooled = data.transpose(2, 0, 1).reshape(n_timepoints * n_trials, n_channels)
    
    for i_s in range(2 ** n_channels):
        state = pyphi.convert.le_index2state(i_s, n_channels)
        state_count = (pooled == np.array(state)).all(axis=-1).sum()
        state_counter[i_s] = state_count
    
    return pyphi.convert.to_2dimensional(tpm), state_counter
