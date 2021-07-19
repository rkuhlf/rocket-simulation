import copy
import pickle

# Parent of all objects that take a config


class PresetObject:
    def __init__(self, config={}):
        overwrite_defaults({}, config)


    def overwrite_defaults(self, config):
        # extract config to self
        self.__dict__.update(config)

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

        self.__init__(config)

    def reset(self):
        self.overwrite_defaults(self.saved_state)
