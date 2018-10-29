import numpy as np
import scipy
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.linear_assignment_ import linear_assignment
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.linear_model import RidgeCV
from scipy import linalg
from scipy.sparse import diags


def scaled_procrustes(X, Y, scaling=False, primal=None):
    """Compute a mixing matrix R and a scaling sc such that
    frobenius norm ||sc RX - Y||^2 is minimized and
    R is an orthogonal matrix
    Parameters
    ----------
    X: (n_timeframes, n_features) nd array
        source data
    Y: (n_timeframes, n_features) nd array
        target data
    scaling: bool
        If scaling is true, computes a floating scaling parameter sc such that:
        ||sc * RX - Y||^2 is minimized and
        - R is an orthogonal matrix
        - sc is a scalar
        If scaling is false sc is set to 1
    primal: bool or None, optional,
         Whether the SVD is done on the YX^T (primal) or Y^TX (dual)
         if None primal is used iff n_features <= n_timeframes

    Returns
    ----------
    R: (n_features, n_features) nd array
        transformation matrix
    sc: int
        scaling parameter
    """
    if np.linalg.norm(X) == 0 or np.linalg.norm(Y) == 0:
        return diags(np.ones(X.shape[1])).tocsr(), 1
    if primal is None:
        primal = X.shape[0] >= X.shape[1]
    if primal:
        A = Y.T.dot(X)
        if A.shape[0] == A.shape[1]:
            A += + 1.e-18 * np.eye(A.shape[0])
        U, s, V = linalg.svd(A, full_matrices=0)
        R = U.dot(V)
    else:  # "dual" mode
        Uy, sy, Vy = linalg.svd(Y, full_matrices=0)
        Ux, sx, Vx = linalg.svd(X, full_matrices=0)
        A = np.diag(sy).dot(Uy.T).dot(Ux).dot(np.diag(sx))
        U, s, V = linalg.svd(A)
        R = Vy.T.dot(U).dot(V).dot(Vx)

    if scaling:
        sc = s.sum() / (np.linalg.norm(X) ** 2)
    else:
        sc = 1
    return R, sc


def optimal_permutation(X, Y):
    """Compute the optmal permutation matrix of X toward Y
    Parameters
    ----------
    X: (n_timeframes, n_features) nd array
        source data
    Y: (n_timeframes, n_features) nd array
        target data

    Returns
    ----------
    permutation : (n_features, n_features) nd array
        transformation matrix
    """
    dist = pairwise_distances(X, Y)
    u = linear_assignment(dist)
    permutation = scipy.sparse.csr_matrix(
        (np.ones(X.shape[0]), (u[:, 0], u[:, 1]))).T
    return permutation


class Alignment(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, Y):
        pass

    def transform(self, X):
        pass


class Identity(Alignment):
    """The simplest kind of alignment to be used as a baseline for benchmarks. RX = X
    """

    def transform(self, X):
        """returns X"""
        return X


class ScaledOrthogonalAlignment(Alignment):
    """Compute a mixing matrix R and a scaling sc such that
    frobenius norm ||sc RX - Y||^2 is minimized and
    R is an orthogonal matrix

    Parameters
    ---------
    scaling : boolean, optional
    Determines whether a scaling parameter is applied to improve transform.
    R : optimal transform
    """

    def init(self, scaling=True):
        self.scaling = scaling
        self.scale = None

    def fit(self, X, Y):
        """ Fit orthogonal R s.t. ||sc RX - Y||^2
        ----------
        X: (n_timeframes, n_features) nd array
            source data
        Y: (n_timeframes, n_features) nd array
            target data
        """
        R, sc = scaled_procrustes(X, Y, scaling=self.scaling)
        self.scale = sc
        self.R = sc * R
        return self

    def transform(self, X):
        """Transform X using optimal transform computed during fit.
        """
        return self.sc * self.R.dot(X)


class RidgeAlignment(Alignment):
    """ Compute a mixing matrix R such that
    frobenius norm || XR - Y ||^2 + alpha ||R||^2 is minimized with built-in cross-validation

    Parameters
    ----------
    alpha : numpy array of shape [n_alphas]
        Array of alpha values to try. Regularization strength; must be a positive float. Regularization
        improves the conditioning of the problem and reduces the variance of
        the estimates. Larger values specify stronger regularization.
        Alpha corresponds to ``C^-1`` in other linear models.
    cv : int, cross-validation generator or an iterable, optional
    Determines the cross-validation splitting strategy. Possible inputs for cv are:
    -None, to use the efficient Leave-One-Out cross-validation
    - integer, to specify the number of folds.
    - An object to be used as a cross-validation generator.
    - An iterable yielding train/test splits.
    """

    def init(self, alphas=[0.1, 1.0, 10.0, 100, 1000], cv=4):
        self.alphas = alphas
        self.cv = cv

    def fit(self, X, Y):
        """ Fit R s.t. || XR - Y ||^2 + alpha ||R||^2 is minimized and choose best alpha through cross-validation
        ----------
        X: (n_timeframes, n_features) nd array
            source data
        Y: (n_timeframes, n_features) nd array
            target data
        """
        self.R = RidgeCV(alphas=self.alphas, fit_intercept=True,
                         normalize=False, scoring=None, cv=self.cv)
        self.R.fit(X, Y)
        return self

    def transform(self, X):
        """Transform X using optimal transform computed during fit.
        """
        return self.R.predict(X)


class Hungarian(Alignment):
    '''Compute the optmal permutation matrix of X toward Y'''

    def fit(self, X, Y):
        '''Parameters
        ----------
        X: (n_timeframes, n_features) nd array
            source data
        Y: (n_timeframes, n_features) nd array
            target data'''
        self.R = optimal_permutation(X, Y)
        return self

    def transform(self, X):
        """Transform X using optimal permutation computed during fit.
        """
        return self.R.dot(X)