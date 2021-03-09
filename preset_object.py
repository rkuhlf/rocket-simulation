# Parent of all objects that take a config


class PresetObject:
    def __init__(self, config={}):
        overwrite_defaults({}, config)



    def overwrite_defaults(self, config):
        # extract config to self
        self.__dict__.update(config)


    def get_config(self):
        # This is an oversimplification, and maybe I should only save the things that have defaults
        return self.__dict__

    def save_preset(self):
        config = self.get_config()

        # Just save a file so that when you load it you get the exact object that you had previously
