# DATA CLASSES AND ENUMS
# Depending on what type of data input we are using, we will want to have an enum entry that is easily serializable to indicate to the object what to do

import re
from enum import Enum, auto

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
    

