from enum import Enum

# Defines all units necessary by mapping them to their abbreviation.
class Units(Enum):
    s = "s"
    kg = "kg"
    kps = "kg s^-1"
    m = "m"
    m2 = "m^2"
    mps = "m s^-1"
    mps2 = "m s^-2"
    flux = "kg m^-2 s^-1"
    radians = "rad"
    rps = "rad s^-1"
    rps2 = "rad s^-2"
    N = "N"
    Pa = "Pa"
    K = "K"
    cals = "cal"
    amount = ""
