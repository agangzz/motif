"""Multivariate Gaussian contour classifier.
"""
import numpy as np
from scipy.stats import boxcox
from scipy.stats import multivariate_normal

from motif.core import ContourClassifier

EPS = 1.0
MAX_SCORE = 10000.0

class MvGaussian(ContourClassifier):
    '''Multivariate Gaussian contour classifier.

    Attributes
    ----------
    rv_pos : scipy.stats._multivariate.multivariate_normal_gen
        A multivariate gaussian modeling the positive class
    rv_neg : scipy.stats._multivariate.multivariate_normal_gen
        A multivariate gaussian modeling the negative class
    n_feats : int
        The number of features
    lmbda : np.array
        Array of length n_features with the optimal lambda.

    '''
    def __init__(self):
        ContourClassifier.__init__(self)

        self.rv_pos = None
        self.rv_neg = None
        self.n_feats = None
        self.lmbda = None

    def predict(self, X):
        """ Compute melodiness score.

        Parameters
        ----------
        X : np.array [n_samples, n_features]
            Features.

        Returns
        -------
        p : np.array [n_samples]
            melodiness scores
        """
        if self.rv_pos is None:
            raise ReferenceError(
                "fit must be called before predict can be called"
            )
        transformed_feats = self._transform(X)
        numerator = self.rv_pos.pdf(transformed_feats)
        denominator = self.rv_neg.pdf(transformed_feats)
        
        ratio = np.zeros(numerator.shape)
        nonzero_denom = np.where(denominator != 0)[0]
        zero_denom = np.where(denominator == 0)[0]
        ratio[nonzero_denom] = (
            numerator[nonzero_denom] / denominator[nonzero_denom]
        )
        ratio[zero_denom] = MAX_SCORE
        ratio[np.where(numerator == 0)[0]] = 0.0
        ratio[ratio > MAX_SCORE] = MAX_SCORE
        return ratio

    def fit(self, X, Y):
        """ Fit class-dependent multivariate gaussians on the training set.

        Parameters
        ----------
        x_train_boxcox : np.array [n_samples, n_features_trans]
            Transformed training features.
        y_train : np.array [n_samples]
            Training labels.

        Returns
        -------
        rv_pos : multivariate normal
            multivariate normal for melody class
        rv_neg : multivariate normal
            multivariate normal for non-melody class
        """
        X_boxcox = self._fit_boxcox(X)
        pos_idx = np.where(Y == 1)[0]
        mu_pos = np.mean(X_boxcox[pos_idx, :], axis=0)
        cov_pos = np.cov(X_boxcox[pos_idx, :], rowvar=0)

        neg_idx = np.where(Y == 0)[0]
        mu_neg = np.mean(X_boxcox[neg_idx, :], axis=0)
        cov_neg = np.cov(X_boxcox[neg_idx, :], rowvar=0)
        rv_pos = multivariate_normal(
            mean=mu_pos, cov=cov_pos, allow_singular=True
        )
        rv_neg = multivariate_normal(
            mean=mu_neg, cov=cov_neg, allow_singular=True
        )
        self.rv_pos = rv_pos
        self.rv_neg = rv_neg

    @property
    def threshold(self):
        """ The threshold determining the positive class.

        Returns
        -------
        threshold : flaot
            melodiness scores
        """
        return 1.0

    @classmethod
    def get_id(cls):
        """ The ContourClassifier identifier

        Returns
        -------
        id : string
            class identifier
        """
        return 'mv_gaussian'

    def _fit_boxcox(self, X):
        """ Transform features using a boxcox transform.

        Parameters
        ----------
        X : np.array [n_samples, n_features]
            Untransformed training features.

        Returns
        -------
        X_boxcox : np.array [n_samples, n_features]
            Transformed training features.
        """
        _, self.n_feats = X.shape

        X_boxcox = np.zeros(X.shape)
        lmbda_opt = np.zeros((self.n_feats,))

        for i in range(self.n_feats):
            X_boxcox[:, i], lmbda_opt[i] = boxcox(
                X[:, i] + EPS
            )
        self.lmbda = lmbda_opt
        return X_boxcox

    def _transform(self, X):
        """ Transform an input feature matrix using the trained boxcox
        parameters.

        Parameters
        ----------
        X : np.array [n_samples, n_features]
            Input features.

        Returns
        -------
        X_boxcox : np.array [n_samples, n_features]
            Transformed features.

        """
        X_boxcox = np.zeros(X.shape)
        for i in range(self.n_feats):
            X_boxcox[:, i] = boxcox(
                X[:, i] + EPS, lmbda=self.lmbda[i]
            )
        return X_boxcox
