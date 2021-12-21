# DECORATORS
# Mostly to make me write less code


def diameter_no_parameters(cls):
    @property
    def twice_radius(self):
        return self.radius * 2
    
    @twice_radius.setter
    def twice_radius(self, d):
        self.radius = d / 2
    
    setattr(cls, "diameter", twice_radius)

    return cls

def diameter_parameters(name="diameter"):
    def wrapper(cls):
        @property
        def twice_radius(self):
            return self.radius * 2
        
        @twice_radius.setter
        def twice_radius(self, d):
            self.radius = d / 2
        
        setattr(cls, name, twice_radius)

        return cls

    return wrapper


def diametered(*args, **kwargs):
    """Apply to a class that already has a radius property to allow the diameter to be set as well"""
    if len(args) == 1 and isinstance(args[0], type):
        return diameter_no_parameters(args[0])
    else:
        return diameter_parameters(*args, **kwargs)