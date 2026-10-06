from dataclasses import dataclass

import numpy as np
import scipy.constants as con
from numpy.polynomial import Polynomial

from sklearn.linear_model import RANSACRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

@dataclass(kw_only=True)
class junction:
    gap_V: float

    x_exp: float | np.ndarray | None = None
    R_Ohm: float | np.ndarray | None = None
    L_H: float | np.ndarray | None = None

    poly_mode: str = 'log'
    poly_order: int = 1
    poly_coe: None = None

    def __post_init__(self):
        if self.R_Ohm is not None:
            self.L_H = self.R2L(R=self.R_Ohm)
        else:
            self.R_Ohm = self.L2R(L=self.L_H)

    def R2x(self, *, R_goal, force_update=False):
        if (self.poly_coe == None) or force_update:
            self.poly_coe, _ = self.fit_R(x_exp=self.x_exp, R_exp=self.R_Ohm, order=self.poly_order, mode=self.poly_mode)

        if self.poly_mode == 'log':
            x_goal = 10 ** (self.poly_coe(np.log10(R_goal)))
        else:
            x_goal = self.poly_coe(R_goal)
        return x_goal

    def R2L(self, *, R):
        L = con.hbar * R / (np.pi * self.gap_V)
        return L

    def L2R(self, *, L):
        R = L * (np.pi * self.gap_V) / con.hbar
        return R

    def fit_R(self, *, x_exp, R_exp, order, mode):
        ind_x = np.argsort(x_exp)
        _x_exp = x_exp[ind_x]
        _R_exp = R_exp[ind_x]

        if mode == 'log':
            x = np.log10(_R_exp)[:, np.newaxis]
            y = np.log10(_x_exp)
        else:
            x = _R_exp[:, np.newaxis]
            y = _x_exp

        model = make_pipeline(
            PolynomialFeatures(order),
            RANSACRegressor(residual_threshold=0.1, max_trials=100)
        )
        model.fit(x, y)

        ransac_step = model.named_steps['ransacregressor']
        final_estimator = ransac_step.estimator_
        full_coefs = final_estimator.coef_.copy()
        full_coefs[0] = final_estimator.intercept_ + full_coefs[0]
        poly_coe = Polynomial(full_coefs)

        inlier_mask = ransac_step.inlier_mask_

        return poly_coe, inlier_mask
