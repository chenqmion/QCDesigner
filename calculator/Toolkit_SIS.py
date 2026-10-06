import numpy as np
import scipy.constants as con
from numpy.polynomial import Polynomial

from sklearn.linear_model import RANSACRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# %%
# Al_gap = 182E-6 * con.e
Al_gap = 217E-6 * con.e

# %%
def R2L(R, gap=Al_gap):
    L = con.hbar / (np.pi * gap) * R
    return L

def L2R(L, gap=Al_gap):
    R = L / (con.hbar / (np.pi * gap))
    return R

# %%
# def fit_R(x_exp, R_exp, order=1, mode='log'):
#     if mode == 'log':
#         poly_coe = Polynomial.fit(np.log10(R_exp), np.log10(x_exp), order)
#     else:
#         poly_coe = Polynomial.fit(R_exp, x_exp, order)
#     return poly_coe

def fit_R(x_exp, R_exp, order=1, mode='log'):
    if mode == 'log':
        x = np.log10(R_exp)[:, np.newaxis]
        y = np.log10(x_exp)
    else:
        x = R_exp[:, np.newaxis]
        y = x_exp

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

def get_x(R_sim, poly_coe, mode):
    if mode == 'log':
        R = 10 ** (poly_coe(np.log10(R_sim)))
    else:
        R = poly_coe(R_sim)
    return R

# %%
def L2w(L, poly_coe, mode, asy=1):
    if asy == 1:
        R = L2R(L)
        w = 1 / np.sqrt(get_x(R, poly_coe, mode))
    else:
        L1 = 2 * L / (1 - asy)
        R1 = L2R(L1)
        w1 = 1 / np.sqrt(get_x(R1, poly_coe, mode))

        if asy == 0:
            w2 = w1
            L2 = L1
        else:
            L2 = (1 - asy) / (1 + asy) * L1
            R2 = L2R(L2)
            w2 = 1 / np.sqrt(get_x(R2, poly_coe, mode))

        w = [w1, w2]
        L = [L1, L2]
    return np.array([w, L])

# #%%
# import numpy as np
# from sklearn.linear_model import RANSACRegressor
# from sklearn.preprocessing import PolynomialFeatures
# from sklearn.pipeline import make_pipeline
#
# X = np.log10(R_exp)[:, np.newaxis]
# y = np.log10(x_exp)
#
# model = make_pipeline(PolynomialFeatures(order), RANSACRegressor())
# model.fit(X, y)
#
# y_pred = model.predict(X)
#
# inlier_mask = model.named_steps['ransacregressor'].inlier_mask_
# outlier_mask = ~inlier_mask
