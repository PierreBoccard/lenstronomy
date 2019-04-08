__author__ = 'sibirrer'

from lenstronomy.Sampling.Likelihoods.time_delay_likelihood import TimeDelayLikelihood
from lenstronomy.Sampling.Likelihoods.image_likelihood import ImageLikelihood
from lenstronomy.Sampling.Likelihoods.position_likelihood import PositionLikelihood
import lenstronomy.Util.class_creator as class_reator


class LikelihoodModule(object):
    """
    this class contains the routines to run a MCMC process
    the key components are:
    - imSim_class: an instance of a class that simulates one (or more) images and returns the likelihood, such as
    ImageModel(), Multiband(), MultiExposure()
    - param_class: instance of a Param() class that can cast the sorted list of parameters that are sampled into the conventions of the imSim_class

    Additional arguments are supported for adding a time-delay likelihood etc (see __init__ definition)
    """
    def __init__(self, kwargs_data_joint, kwargs_model, param_class, image_likelihood=True, check_bounds=True, check_solver=False,
                 point_source_likelihood=False, position_uncertainty=0.004, check_positive_flux=False,
                 solver_tolerance=0.001, force_no_add_image=False, source_marg=False, restrict_image_number=False,
                 max_num_images=None, bands_compute=None, time_delay_likelihood=False,
                 force_minimum_source_surface_brightness=False, flux_min=0):
        """
        initializing class


        :param param_class: instance of a Param() class that can cast the sorted list of parameters that are sampled into the
        conventions of the imSim_class
        :param image_likelihood: bool, option to compute the imaging likelihood
        :param check_bounds:  bool, option to punish the hard bounds in parameter space
        :param check_solver: bool, option to check whether point source position solver finds a solution to match all
         the image positions in the same source plane coordinate
        :param point_source_likelihood: bool, additional likelihood term of the predicted vs modelled point source position
        :param flaot, position_uncertainty: 1-sigma Gaussian uncertainty on the point source position
        (only used if point_source_likelihood=True)
        :param check_positive_flux: bool, option to punish models that do not have all positive linear amplitude parameters
        :param solver_tolerance: float, punishment of check_solver occures when image positions are predicted further
        away than this number
        :param force_no_add_image: bool, if True: computes ALL image positions of the point source. If there are more
        images predicted than modelled, a punishment occures
        :param source_marg: marginalization addition on the imaging likelihood based on the covariance of the infered
        linear coefficients
        :param restrict_image_number: bool, if True: computes ALL image positions of the point source. If there are more
        images predicted than indicated in max_num_images, a punishment occures
        :param max_num_images: int, see restrict_image_number
        :param bands_compute: list of bools with same length as data objects, indicates which "band" to include in the fitting
        :param time_delay_likelihood: bool, if True computes the time-delay likelihood of the FIRST point source
        :param force_minimum_source_surface_brightness: bool, if True, evaluates the source surface brightness on a grid
        and evaluates if all positions have positive flux
        """
        multi_band_list = kwargs_data_joint.get('multi_band_list', [])
        multi_band_type = kwargs_data_joint.get('image_type', 'single-band')
        time_delays_measured = kwargs_data_joint.get('time_delays_measured', None)
        time_delays_uncertainties = kwargs_data_joint.get('time_delays_uncertainties', None)

        self.param = param_class
        self._lower_limit, self._upper_limit = self.param.param_limits()
        lens_model_class, source_model_class, lens_light_model_class, point_source_class = class_reator.create_class_instances(**kwargs_model)
        self.PointSource = point_source_class

        self._time_delay_likelihood = time_delay_likelihood
        if self._time_delay_likelihood is True:
            self.time_delay_likelihood = TimeDelayLikelihood(time_delays_measured, time_delays_uncertainties,
                                                             lens_model_class, point_source_class, param_class)

        self._image_likelihood = image_likelihood
        if self._image_likelihood is True:

            self.image_likelihood = ImageLikelihood(multi_band_list, multi_band_type, lens_model_class,
                                                    source_model_class, lens_light_model_class,
                                                    point_source_class, bands_compute=bands_compute,
                                                    source_marg=source_marg,
                                                    force_minimum_source_surface_brightness=force_minimum_source_surface_brightness,
                                                    flux_min=flux_min)
        self._position_likelihood = PositionLikelihood(point_source_class, param_class, point_source_likelihood,
                                                       position_uncertainty, check_solver, solver_tolerance,
                                                       force_no_add_image, restrict_image_number, max_num_images)
        self._check_positive_flux = check_positive_flux
        self._check_bounds = check_bounds

    def _reset_point_source_cache(self, bool=True):
        self.PointSource.delete_lens_model_cach()
        self.PointSource.set_save_cache(bool)
        if self._image_likelihood is True:
            self.image_likelihood.reset_point_source_cache(bool)

    def logL(self, args):
        """
        routine to compute X2 given variable parameters for a MCMC/PSO chain
        """
        #extract parameters
        kwargs_lens, kwargs_source, kwargs_lens_light, kwargs_ps, kwargs_cosmo = self.param.args2kwargs(args)
        #generate image and computes likelihood
        self._reset_point_source_cache(bool=True)
        logL = 0
        if self._check_bounds is True:
            penalty, bound_hit = self.check_bounds(args, self._lower_limit, self._upper_limit)
            logL -= penalty
            if bound_hit:
                return logL, None
        if self._image_likelihood is True:
            logL += self.image_likelihood.logL(kwargs_lens, kwargs_source, kwargs_lens_light, kwargs_ps)
        if self._time_delay_likelihood is True:
            logL += self.time_delay_likelihood.logL(kwargs_lens, kwargs_ps, kwargs_cosmo)
        if self._check_positive_flux is True:
            bool = self.param.check_positive_flux(kwargs_source, kwargs_lens_light, kwargs_ps)
            if bool is False:
                logL -= 10**10
        logL += self._position_likelihood.logL(kwargs_lens, kwargs_ps, kwargs_cosmo)
        self._reset_point_source_cache(bool=False)
        return logL, None

    @staticmethod
    def check_bounds(args, lowerLimit, upperLimit):
        """
        checks whether the parameter vector has left its bound, if so, adds a big number
        """
        penalty = 0
        bound_hit = False
        for i in range(0, len(args)):
            if args[i] < lowerLimit[i] or args[i] > upperLimit[i]:
                penalty = 10**15
                bound_hit = True
        return penalty, bound_hit

    @property
    def num_data(self):
        """

        :return: number of independent data points in the combined fitting
        """
        num_data = 0
        if self._image_likelihood is True:
            num_data += self.image_likelihood.num_data
        if self._time_delay_likelihood is True:
            num_data += self.time_delay_likelihood.num_data
        return num_data

    @property
    def param_limits(self):
        return self._lower_limit, self._upper_limit

    def effectiv_num_data_points(self, kwargs_lens, kwargs_source, kwargs_lens_light, kwargs_ps):
        """
        returns the effective number of data points considered in the X2 estimation to compute the reduced X2 value
        """
        num_linear = 0
        if self._image_likelihood is True:
            num_linear = self.image_likelihood.num_param_linear(kwargs_lens, kwargs_source, kwargs_lens_light, kwargs_ps)
        num_param, _ = self.param.num_param()
        return self.num_data - num_param - num_linear

    def __call__(self, a):
        return self.logL(a)

    def likelihood(self, a):
        return self.logL(a)

    def computeLikelihood(self, ctx):
        logL, _ = self.logL(ctx.getParams())
        return logL

    def setup(self):
        pass


class FluxLikelihood(object):
    """
    likelihood class for magnification of multiply lensed images
    """
    def __init__(self, point_source_class, lens_model_class):
        pass


