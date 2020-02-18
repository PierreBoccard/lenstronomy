import lenstronomy.Util.constants as const
import numpy as np


class Cosmo(object):
    """
    cosmological quantities
    """
    def __init__(self, D_d, D_s, D_ds):
        self.dd = float(D_d)  # angular diameter distance from observer to deflector in physical Mpc
        self.ds = float(D_s)  # angular diameter distance from observer to source in physical Mpc
        self.dds = float(D_ds)  # angular diameter distance from deflector to source in physical Mpc

    def arcsec2phys_lens(self, theta):
        """
        converts are seconds to physical units on the deflector
        :param theta:
        :return:
        """
        return theta * const.arcsec * self.dd

    @property
    def epsilon_crit(self):
        """
        returns the critical projected mass density in units of M_sun/Mpc^2 (physical units)
        """
        const_SI = const.c**2 / (4*np.pi * const.G)  #c^2/(4*pi*G) in units of [kg/m]
        conversion = const.Mpc / const.M_sun  # converts [kg/m] to [M_sun/Mpc]
        pre_const = const_SI*conversion   #c^2/(4*pi*G) in units of [M_sun/Mpc]
        Epsilon_Crit = self.ds / (self.dd * self.dds) * pre_const #[M_sun/Mpc^2]
        return Epsilon_Crit
