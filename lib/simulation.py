# SIMULATION CLASS
# This is the file for the basic connections between a rocket, a logger, and an environment
# It doesn't really do much math, but there are a few basic utilities that help in other places

from abc import ABCMeta, abstractmethod

from src.rocketparts.motorparts.grain import Grain
from src.rocketparts.motor import Motor
from lib.presetObject import PresetObject

from src.rocket import Rocket
from lib.general import magnitude
from lib.logging.logger import Logger
from lib.verbosity import Verbosity
from src.environment import Environment


class Simulation(PresetObject, metaclass=ABCMeta):
    """
    Provide a base class for all frame-by-frame iterative simulations.
    They always provide integration with a logger.
    Don't instantiate this class, inherit from it.
    """

    def override_subobjects(self):
        """
        Ensure that all of the subobjects the simulation references have the correct memory addresses in there. This should almost always be overriden.
        """
        if self.logger is not None:
            self.logger.simulation = self

    def __init__(self, **kwargs):
        """
        You could potentially pass in a logger, but a default one will be created for you
        Other variables are max_frames and stop_on_error.
        The most important factor is the time_increment - check out some of the timeStudies to see the effect.
        """
        # All frame-based simulations need frames and time.
        self.max_frames = -1
        self.frames = 0
        self.time = 0
        self.time_increment = 0.01 # seconds

        self.stop_on_error = True

        self.logger = Logger(self)
        self.automatically_save = True

        self.verbosity = Verbosity.NORMAL

        super().overwrite_defaults(**kwargs)

        self.override_subobjects()

    def reset(self):
        super().reset()

        # This is very necessary and it kind of makes resetting the other stuff pointless
        self.override_subobjects()

    def copy(self):
        # FIXME: I think I designed it like this to work with one of the genetic simulations, I need to make it better so that I can use it with a config
        return Simulation(logger=self.logger)


    @property
    def logger(self):
        if not hasattr(self, "_logger"):
            self._logger = None
        
        return self._logger

    @logger.setter
    def logger(self, l):
        self._logger = l

        self.override_subobjects()
    
    def initialize_simulation(self):
        pass

    def simulate_step(self):
        if self.logger is not None:
            # Also saves the row
            self.logger.handle_frame()

        self.frames += 1
        self.time += self.time_increment

    def end(self):
        if self.logger is not None and self.automatically_save:
            self.logger.save_to_csv()

    @abstractmethod
    def is_finished(self):
        """This should be overridden, that way the simulation knows when to stop."""
        pass

    @property
    def frames_remaining(self):
        """Return a boolean that is false if we have reached the maximum number of frames, given that the max isn't -1"""
        return self.max_frames == -1 or self.max_frames > self.frames

    def run_simulation(self):
        try:
            if self.stop_on_error:
                while not self.is_finished() and self.frames_remaining:
                    self.simulate_step()
            else:
                try:
                    while not self.is_finished() and self.frames_remaining:
                        self.simulate_step()
                except (Exception) as e:
                    print(e)
                
        finally:
            self.end()

