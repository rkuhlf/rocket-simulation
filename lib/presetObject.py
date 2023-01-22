# DEFINE A PRESET OBJECT
# Parent of all objects that take override self with kwargs
# Each should be saveable individually and as a whole

import copy
import pickle
from abc import ABCMeta

class PresetObject(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.overwrite_defaults(**kwargs)


    def overwrite_defaults(self, **kwargs):
        # extract kwargs to self
        for key, value in kwargs.items():
            # Automatically calls the setter if it is defined            
            setattr(self, key, value)
        
        
        # self.__dict__.update(**kwargs)

        self.update_saved_state()

    def update_saved_state(self):
        self.saved_state = copy.deepcopy(self.__dict__)


    def get_config(self):
        """Get the saved self variable from right after initialization"""
        # This is an oversimplification, and maybe I should only save the things that have defaults
        return self.saved_state

    def save_preset(self, name):
        # Using pickle because I'm not sure json plays nice with numpy
        config = self.get_config()

        # Just save a file so that when you load it you get the exact self object that you had previously
        with open('Data/Input/Presets/' + name + '.pkl', 'wb') as f:
            pickle.dump(config, f, pickle.HIGHEST_PROTOCOL)


    def load_preset(self, name):
        # might be better to make these static methods
        config = {}

        with open('Data/Input/Presets/' + name + '.pkl', 'rb') as f:
            config = pickle.load(f)

        self.__init__(**config)

    def reset(self):
        self.overwrite_defaults(self.saved_state)

    def copy(self):
        return copy.deepcopy(self)


