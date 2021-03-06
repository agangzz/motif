"""Bitteli feature extractor.
"""
import numpy as np

from motif.core import FeatureExtractor
from motif.feature_extractors import utils


class BitteliFeatures(FeatureExtractor):
    '''Bitteli feature extractor

    Attributes
    ----------
    ref_hz : float
        Reference frequency (Hz) for converting to cents.
    poly_degree : int
        Polynomial fit degree.
    min_freq : float
        Minimum possible vibrato frequency (Hz).
    max_freq : float
        Maximum possible vibrato frequency (Hz).
    freq_step : float
        Step in Hz between frequencies to search.
    vibrato_threshold : float
        Threshold on the average vibrato residual to be considered vibrato.

    '''
    def __init__(self, ref_hz=55.0, poly_degree=5, min_freq=3, max_freq=30,
                 freq_step=0.1, vibrato_threshold=0.25):
        '''Init method

        Parameters
        ----------
        ref_hz : float
            Reference frequency (Hz) for converting to cents.
        poly_degree : int
            Polynomial fit degree.
        min_freq : float
            Minimum possible vibrato frequency (Hz).
        max_freq : float
            Maximum possible vibrato frequency (Hz).
        freq_step : float
            Step in Hz between frequencies to search.
        vibrato_threshold : float
            Threshold on the average vibrato residual to be considered vibrato.

        '''
        self.ref_hz = ref_hz
        self.poly_degree = poly_degree
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.freq_step = freq_step
        self.vibrato_threshold = vibrato_threshold
        FeatureExtractor.__init__(self)

    def get_feature_vector(self, times, freqs_hz, salience, sample_rate):
        """Get feature vector for a contour.

        Parameters
        ----------
        times : np.array
            Contour times
        freqs_hz : np.array
            Contour frequencies (Hz)
        salience : np.array
            Contour salience
        sample_rate : float
            Contour sample rate.

        Returns
        -------
        feature_vector : np.array
            Feature vector.

        """
        freqs_cents = utils.hz_to_cents(freqs_hz, ref_hz=self.ref_hz)

        features = [
            utils.get_contour_shape_features(
                times, freqs_cents, sample_rate, poly_degree=self.poly_degree,
                min_freq=self.min_freq, max_freq=self.max_freq,
                freq_step=self.freq_step,
                vibrato_threshold=self.vibrato_threshold),
            utils.get_polynomial_fit_features(
                times - np.mean(times), salience, n_deg=self.poly_degree,
                norm=False
            ),
            utils.get_contour_duration(times),
            utils.get_std(freqs_cents),
            utils.get_range(freqs_cents),
            utils.get_total_variation(freqs_cents)/len(freqs_cents),
            utils.get_std(salience),
            utils.get_range(salience),
            utils.get_total_variation(salience)/len(freqs_cents)
        ]

        return np.concatenate(features)

    @property
    def feature_names(self):
        """Get feature names.

        Returns
        -------
        feature_names : list
            List of feature names.

        """
        feature_names = [
            'vibrato rate',
            'vibrato extent',
            'vibrato coverage',
            'vibrato coverage - beginning',
            'vibrato coverage - middle',
            'vibrato coverage - end',
            '0th polynomial coeff - freq',
            '1st polynomial coeff - freq',
            '2nd polynomial coeff - freq',
            '3rd polynomial coeff - freq',
            '4th polynomial coeff - freq',
            '5th polynomial coeff - freq',
            'polynomial fit residual - freq',
            'overall model fit residual - freq',
            '0th polynomial coeff - salience',
            '1st polynomial coeff - salience',
            '2nd polynomial coeff - salience',
            '3rd polynomial coeff - salience',
            '4th polynomial coeff - salience',
            '5th polynomial coeff - salience',
            'polynomial fit residual - salience',
            'duration',
            'pitch stddev (cents)',
            'pitch range (cents)',
            'pitch average variation',
            'salience stdev',
            'salience range',
            'salience average variation'
        ]
        return feature_names

    @classmethod
    def get_id(cls):
        """ The FeatureExtractor identifier

        Returns
        -------
        id : string
            class identifier
        """
        return 'bitteli'
