import warnings

from scipy.stats import ttest_ind as ttest
import numpy as np
import matplotlib.pyplot as plt


def analyse(project, kernel, sub_graphs):
    """
    Analyse traces found within a project TVLA style.
    :param project: ChipWhisperer project file.
    """
    num_traces = len(project.traces)
    # TVLA requires test to be run twice on independent data sets, so partition the traces.
    print('Performing TVLA analysis...')
    test1, test2 = project.traces[:num_traces // 2], project.traces[num_traces // 2:]
    print('Performing two independent tests with size: ' + str(len(test1)) + ' and ' + str(len(test2)))
    distances1 = _welch_t_test(test1, kernel, sub_graphs)
    distances2 = _welch_t_test(test2, kernel, sub_graphs)

    result = any([_threshold(val1) and _threshold(val2) for val1, val2 in zip(distances1, distances2)])

    _plot_results(distances1, distances2, result, kernel)

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


def _welch_t_test(traces, kernel, sub_graphs):
    """
    Perform the welch t test on traces.
    :param traces: traces to partition and test.
    :return: boolean list representing possible leakage.
    """
    # Define the fixed input plaintext for tvla here.
    fixed_plaintext = bytearray.fromhex("da 39 a3 ee 5e 6b 4b 0d 32 55 bf ef 95 60 18 90")
    # Sort traces into groups based on plaintext derivation
    fixed_group = np.array([trace.wave for trace in traces if trace.textin == fixed_plaintext])
    random_group = np.array([trace.wave for trace in traces if trace.textin != fixed_plaintext])
    # Compute the t test point wise (i.e. for each point compare power values between all traces => measure on 0th axis)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        distances = np.nan_to_num(ttest(fixed_group, random_group, axis=0, equal_var=False)[0])
        if sub_graphs:
            plt.plot(distances)
            plt.xlabel('Sample Number')
            plt.ylabel('t value')
            plt.title(kernel.split('/')[-1].split('.')[0])
            plt.show()
    return distances


def _plot_results(distances1, distances2, fail, kernel):
    """
    Plot results to figure.
    :param distances1: results from 1st t test
    :param distances2: results from 2nd t test
    :param fail: whether the test failed
    """
    outcome = ['OK!', 'FAIL!']
    plt.xlabel('Sample Number')
    plt.ylabel('t value')
    plt.axhline(4.5, color='r')
    plt.axhline(-4.5, color='r')
    plt.title(kernel.split('/')[-1].split('.')[0] + ' = ' + outcome[int(fail)])
    plt.plot(distances1, label='t-test 1', color='m')
    plt.plot(distances2, label='t-test 2', color='b')
    plt.legend(loc='best')
    plt.show()

# [1] : https://www.rambus.com/test-vector-leakage-assessment-tvla-derived-test-requirements-dtr-with-aes/
