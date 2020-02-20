__author__ = 'sibirrer'


from lenstronomy.LightModel.Profiles.sersic import Sersic, SersicElliptic, CoreSersic
import lenstronomy.Util.param_util as param_util
import numpy as np
import pytest
import numpy.testing as npt


class TestSersic(object):
    """
    tests the Gaussian methods
    """
    def setup(self):
        self.sersic = Sersic(smoothing=0.02)
        self.sersic_elliptic = SersicElliptic(smoothing=0.02)
        self.core_sersic = CoreSersic(smoothing=0.02)

    def test_sersic(self):
        x = np.array([1])
        y = np.array([2])
        I0_sersic = 1
        R_sersic = 1
        n_sersic = 1
        center_x = 0
        center_y = 0
        values = self.sersic.function(x, y, I0_sersic, R_sersic, n_sersic, center_x, center_y)
        npt.assert_almost_equal(values[0], 0.12658651833626802, decimal=6)
        x = np.array([0])
        y = np.array([0])
        values = self.sersic.function( x, y, I0_sersic, R_sersic, n_sersic, center_x, center_y)
        npt.assert_almost_equal(values[0],  5.1482559148107292, decimal=2)

        x = np.array([2,3,4])
        y = np.array([1,1,1])
        values = self.sersic.function( x, y, I0_sersic, R_sersic, n_sersic, center_x, center_y)
        npt.assert_almost_equal(values[0], 0.12658651833626802, decimal=6)
        npt.assert_almost_equal(values[1], 0.026902273598180083, decimal=6)
        npt.assert_almost_equal(values[2], 0.0053957432862338055, decimal=6)

        value = self.sersic.function(1000, 0, I0_sersic, R_sersic, n_sersic, center_x, center_y)
        npt.assert_almost_equal(value, 0, decimal=8)

    def test_symmetry_r_sersic(self):
        x = np.array([2,3,4])
        y = np.array([1,1,1])
        I0_sersic = 1
        R_sersic1 = 1
        R_sersic2 = 0.1
        n_sersic = 1
        center_x = 0
        center_y = 0
        values1 = self.sersic.function(x*R_sersic1, y*R_sersic1, I0_sersic, R_sersic1, n_sersic, center_x, center_y)
        values2 = self.sersic.function(x*R_sersic2, y*R_sersic2, I0_sersic, R_sersic2, n_sersic, center_x, center_y)
        npt.assert_almost_equal(values1[0], values2[0], decimal=6)
        npt.assert_almost_equal(values1[1], values2[1], decimal=6)
        npt.assert_almost_equal(values1[2], values2[2], decimal=6)

    def test_sersic_center(self):
        x = 0.01
        y = 0.
        I0_sersic = 1
        R_sersic = 0.1
        n_sersic = 4.
        center_x = 0
        center_y = 0
        values = self.sersic.function(x, y, I0_sersic, R_sersic, n_sersic, center_x, center_y)
        npt.assert_almost_equal(values, 12.688073819377406, decimal=6)

    def test_sersic_elliptic(self):
        x = np.array([1])
        y = np.array([2])
        I0_sersic = 1
        R_sersic = 1
        n_sersic = 1
        phi_G = 1
        q = 0.9
        e1, e2 = param_util.phi_q2_ellipticity(phi_G, q)
        center_x = 0
        center_y = 0
        values = self.sersic_elliptic.function(x, y, I0_sersic, R_sersic, n_sersic, e1, e2, center_x, center_y)
        npt.assert_almost_equal(values[0], 0.12595366113005077, decimal=6)
        x = np.array([0])
        y = np.array([0])
        values = self.sersic_elliptic.function(x, y, I0_sersic, R_sersic, n_sersic, e1, e2, center_x, center_y)
        npt.assert_almost_equal(values[0], 5.1482553482055664, decimal=2)

        x = np.array([2,3,4])
        y = np.array([1,1,1])
        values = self.sersic_elliptic.function(x, y, I0_sersic, R_sersic, n_sersic, e1, e2, center_x, center_y)
        npt.assert_almost_equal(values[0], 0.11308277793465012, decimal=6)
        npt.assert_almost_equal(values[1], 0.021188620675507107, decimal=6)
        npt.assert_almost_equal(values[2], 0.0037276744362724477, decimal=6)

    def test_core_sersic(self):
        x = np.array([1])
        y = np.array([2])
        I0 = 1
        Rb = 1
        Re = 2
        gamma = 3
        n = 1
        phi_G = 1
        q = 0.9
        e1, e2 = param_util.phi_q2_ellipticity(phi_G, q)
        center_x = 0
        center_y = 0
        values = self.core_sersic.function(x, y, I0, Rb, Re, n, gamma, e1, e2, center_x, center_y)
        npt.assert_almost_equal(values[0], 0.10338957116342086, decimal=8)
        x = np.array([0])
        y = np.array([0])
        values = self.core_sersic.function(x, y, I0, Rb, Re, n, gamma, e1, e2, center_x, center_y)
        npt.assert_almost_equal(values[0], 187852.14004235074, decimal=0)

        x = np.array([2,3,4])
        y = np.array([1,1,1])
        values = self.core_sersic.function(x, y, I0, Rb, Re, n, gamma, e1, e2, center_x, center_y)
        npt.assert_almost_equal(values[0], 0.09255079955772508, decimal=6)
        npt.assert_almost_equal(values[1], 0.01767817014938002, decimal=6)
        npt.assert_almost_equal(values[2], 0.0032541063777438853, decimal=6)

    def test_total_flux(self):
        r_eff = 0.2
        I_eff = 1.
        n_sersic = 4
        flux = self.sersic._total_flux(r_eff, I_eff, n_sersic)
        npt.assert_almost_equal(flux, 0.9065917451904356, decimal=5)


if __name__ == '__main__':
    pytest.main()
