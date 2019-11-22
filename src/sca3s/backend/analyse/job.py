import warnings, gzip, shutil

from scipy.stats import ttest_ind as ttest
import numpy as np
import matplotlib.pyplot as plt
import h5py
import requests
from sca3s import backend as be


class JobImp(be.share.job.JobAbs):
    """
    Class defining the implementation of TVLA analysis.
    """

    def __init__(self, conf, path, log):
        super().__init__(conf, path, log)

        self.conf = conf
        self.path = path
        self.log = log

    def process_prologue(self):
        """
        Analysis does not need a prologue.
        """
        pass

    def process(self):
        """
        Main wrapper function for the analyis tasks.
        """
        self._download_traces()
        self._analyse(False)

    def process_epilogue(self):
        """
        Analysis doesn't need an epilogue.
        """
        pass

    def _download_traces(self):
        """
        Download the acquisition data set from the signed S3 url present in the manifest.
        """
        self.log.indent_inc(message='downloading acquisition traces.')

        url = self.conf.get('traces_url')
        response = requests.get(url)
        self.log.info('writing traces into ' + self.path + '/traces.hdf5.gz')
        with open(self.path + '/traces.hdf5.gz', 'wb') as fd:
            fd.write(response.content)

        self.log.info('extracting traces into ' + self.path + '/traces.hdf5')
        with gzip.open(self.path + '/traces.hdf5.gz', 'rb') as fd_in:
            with open(self.path + '/traces.hdf5', 'wb') as fd_out:
                shutil.copyfileobj(fd_in, fd_out)

        self.log.indent_dec()

    def _analyse(self, sub_graphs):
        """
        Analyse traces found within a project TVLA style.
        """
        # TVLA requires test to be run twice on independent data sets, so partition the traces.
        self.log.indent_inc(message='performing TVLA analysis.')

        self.log.info('attempting to open hdf5 file.')
        data = h5py.File(self.path + '/traces.hdf5', 'r')
        self.log.info('performing TVLA t-test.')
        distances = self._welch_t_test(data, sub_graphs)
        data.close()
        result = any(distances)
        self.log.info('graphing results.')
        self._plot_results(distances, result)

        if result:
            self.log.info('Test concluded that this implementation is leaking!')
        else:
            self.log.info('Test concluded that this implementation looks ok :)')

        self.log.indent_dec()

    def _threshold(self, number):
        """
        Simple threshold calculator for 4.5 std deviation test.
        :param number: input number.
        :return: Boolean relating to whether the confidence interval is exceeded.
        """
        if abs(number) > 4.5:
            return True
        return False

    def _welch_t_test(self, data, sub_graphs):
        """
        Perform the welch t test on traces.
        :param traces: traces to partition and test.
        :return: boolean list representing possible leakage.
        """
        # Sort traces into groups based on plaintext derivation
        crop = len(data['trace/signal'][data['crop/signal'][0]][0])
        for i in range(2000):
            candidate = len(data['trace/signal'][data['crop/signal'][i]][0])
            if candidate < crop:
                crop = candidate
        fixed_group = np.array([data['trace/signal'][data['crop/signal'][i]][0][:crop] for i in data['tvla']['lhs']])
        random_group = np.array([data['trace/signal'][data['crop/signal'][i]][0][:crop] for i in data['tvla']['rhs']])

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

    def _plot_results(self, distances, fail):
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
