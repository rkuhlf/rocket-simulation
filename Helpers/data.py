# DATA CLASSES AND ENUMS
# Depending on what type of data input we are using, we will want to have an enum entry that is easily serializable to indicate to the object what to do

import re
from enum import Enum, auto
import numpy as np


from Helpers.general import interpolate

#region CONSTANTS
inputs_path = "./Data/Input/"
outputs_path = "./Data/Output/"

#endregion



# Mass object needs a data type for default (calculated), constant (not calculated), lookup (I am really concerned that I will end up having to have multiple input types for look up, like AOA_MACH; causes clutter), and function (once again, I do not want to have multiple function look ups)
# There is no need for an individual lookup type. If the user wants to look up the thing they, can do the lookup themselves in the inputted function
class DataType(Enum):
    DEFAULT = auto()
    CONSTANT = auto()
    FUNCTION_TIME = auto()
    FUNCTION_FLUX = auto()
    # In the injector, you define the function for flow rate in terms of the injector itself, that way you have access to all of the properties you need
    # It should expect an injector object to be passed in
    FUNCTION_INJECTOR = auto()
    FUNCTION_MACH_ALPHA = auto()


def fahrenheit_from_kelvin(kelvin):
    return (kelvin - 273.15) * 9/5 + 32

def reimann_sum(x, y):
    total = 0
    for i in range(len(x) - 1):
        # Use a trapezoidal reimann sum to approximate the integral
        total += (x[i + 1] - x[i]) * (y[i] + y[i + 1]) / 2

    return total


def nested_dictionary_lookup(dictionary, key):
    if len(key) == 0:
        raise Exception("Empty key passed in")

    key_array = re.split("\.|/|,", key)

    return nested_dictionary_lookup_array(dictionary, key_array)


def nested_dictionary_lookup_array(dictionary, key_array):
    """Helper for regular nested lookup, uses array of keys"""
    if len(key_array) == 0:
        raise Exception("Empty key array passed in")

    current = key_array[0]

    if isinstance(dictionary, object):
        if len(key_array) == 1:
            return getattr(dictionary, current)
    
        del key_array[0]

        return nested_dictionary_lookup_array(getattr(dictionary, current), key_array)

    else:
        if len(key_array) == 1:
            return dictionary[current]
    
        del key_array[0]

        return nested_dictionary_lookup_array(dictionary[current], key_array)
    

# FIXME: rename from safe
def interpolated_lookup(dataframe, key, value, lookup_key, safe=False):
    before_keys = dataframe[dataframe[key] <= value]
    if safe and len(before_keys) == 0:
        # There is nothing to look up in the table that is lower than that value
        return dataframe[dataframe[key] == dataframe[key].min()][lookup_key].values[0]


    before_key = before_keys.iloc[-1]


    after_keys = dataframe[dataframe[key] >= value]
    if safe and len(after_keys) == 0:
        # There is nothing to look up in the table that is bigger than that value
        return dataframe[dataframe[key] == dataframe[key].max()][lookup_key].values[0]

    after_key = after_keys.iloc[0]

    return interpolate(value, before_key[key], after_key[key], before_key[lookup_key], after_key[lookup_key])


def interpolated_lookup_2D(dataframe, key1, key2, value1, value2, lookup_key):
    """
    The dataframe must be sorted first by key1 and second by key2
    value1 and value2 match up to the corresponding key names
    This is basically a really slow, custom implementation of bisplev
    """


    # Since it is sorted, we can do the ones right on the edge closest to it
    before_key1 = dataframe[dataframe[key1] <= value1].iloc[-1]
    value_before_value1 = before_key1[key1]
    value1_isoline_before = dataframe[dataframe[key1] == value_before_value1]

    before_value = interpolated_lookup(value1_isoline_before, key2, value2, lookup_key)



    # We have to do two so that I can do a double interpolation
    after_key1 = dataframe[dataframe[key1] >= value1].iloc[-1]
    value_after_value1 = after_key1[key1]
    value1_isoline_after = dataframe[dataframe[key1] == value_after_value1]

    after_value = interpolated_lookup(value1_isoline_after, key2, value2, lookup_key)

    return interpolate(value1, value_before_value1, value_after_value1, before_value, after_value)

    # thrust = interpolate(current_time, previous_thrust["time"], next_thrust["time"], previous_thrust["thrust"], next_thrust["thrust"])