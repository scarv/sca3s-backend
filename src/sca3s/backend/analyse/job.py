import warnings, os

from scipy.stats import ttest_ind as ttest
import numpy as np
import matplotlib.pyplot as plt
import h5py
from src.sca3s.backend.analyse.api import APIImp


def analyse(file, sub_graphs):
    """
    Analyse traces found within a project TVLA style.
    :param project: ChipWhisperer project file.
    """
    # TVLA requires test to be run twice on independent data sets, so partition the traces.
    print('Performing TVLA analysis...')
    data = h5py.File(file,'r')
    distances = _welch_t_test(data, sub_graphs)
    data.close()
    result = any(distances)
    _plot_results(distances, result)

    print('\nTEST RESULT')
    if result:
        print('Test concluded that this implementation is leaking!')
    else:
        print('Test concluded that this implementation looks ok :)')


def _threshold(number):
    """
    Simple threshold calculator for 4.5 std deviation test.
    :param number: input number.
    :return: Boolean relating to whether the confidence interval is exceeded.
    """
    if abs(number) > 4.5:
        return True
    return False


def _welch_t_test(data, sub_graphs):
    """
    Perform the welch t test on traces.
    :param traces: traces to partition and test.
    :return: boolean list representing possible leakage.
    """
    # Sort traces into groups based on plaintext derivation
    crop = len( data['trace/signal'][ data['crop/signal'][0] ][0] )
    for i in range(2000):
        candidate = len( data['trace/signal'][ data['crop/signal'][i] ][0] )
        if candidate < crop:
            crop = candidate
    fixed_group  = np.array([data['trace/signal'][ data['crop/signal'][i] ][0][:crop] for i in data['tvla']['lhs']])
    random_group = np.array([data['trace/signal'][ data['crop/signal'][i] ][0][:crop] for i in data['tvla']['rhs']])


    # Compute the t test point wise (i.e. for each point compare power values between all traces => measure on 0th axis)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        distances = np.nan_to_num(ttest(fixed_group, random_group, axis=0, equal_var=False)[0])
        if sub_graphs:
            plt.plot(distances)
            plt.xlabel('Sample Number')
            plt.ylabel('t value')
            plt.title('TVLA T Test Graph')
            plt.show()
    return distances


def _plot_results(distances, fail):
    """
    Plot results to figure.
    :param distances1: results from 1st t test
    :param distances2: results from 2nd t test
    :param fail: whether the test failed
    """
    outcome = ['OK!', 'FAIL!']
    plt.xlabel('Sample Number')
    plt.ylabel('t value')
    plt.axhline(4.5, label='threshold', color='r')
    plt.axhline(-4.5, color='r')
    plt.title('TVLA Test Result: ' + outcome[int(fail)])
    plt.plot(distances, label='t-test values', color='m')
    # plt.plot(distances2, label='t-test 2', color='b')
    plt.legend(loc='best')
    plt.show()

# [1] : https://www.rambus.com/test-vector-leakage-assessment-tvla-derived-test-requirements-dtr-with-aes/


if __name__ == "__main__":
    analyse('/home/james/Developer/sca3s-backend/acquire.hdf5', False)