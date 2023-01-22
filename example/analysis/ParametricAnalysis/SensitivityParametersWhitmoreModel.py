# How important is it to get accurate numbers for those things whitmore says you need

# CONCLUSION:
# The regression rate is highly dependent on the Prandtl number; if you are going to use a constant one, be confident
# Length is not nearly as important (it only affects Reynolds number); basically causes a max change of 1 mm/s depending on how much we change
# The r-dot is basically directly proportional to temperature. Could be anywhere from 0.2 to 1.15 mm/s, based on 500 to 3000 K. Probably closest to 0.75. Presumably, the same thing is true of specific heat - the regression is directly proportional to it
# Should really try to get viscosity correct - I would say that we have a range of something like 4e-5 to 8e-5, but it is extremely hard to tell with the temperature variation through the chamber and the various combustion products and the not pure compositions. Those values give a range of 0.88 mm/s to 1.01 mm/s. Probably closest to 0.95 mm/s
# Latent heat of vaporization is really important to get correct

import numpy as np
import matplotlib.pyplot as plt
from src.rocketparts.motorparts.grain import constant, whitmore_regression_model
# from src.rocketparts.motorparts.grain import HTPBGrain as Grain
from src.rocketparts.motorparts.grain import ABSGrain as Grain


def new_grain():
    g = Grain()
    g.regression_rate_function = whitmore_regression_model
    g.update_regression(3, 0, flame_temperature=2400)
    print(f"FLUX: {g.get_flux()}")

    return g

def display_prandtl():
    g = new_grain()
    prandtls = np.linspace(0.1, 2.5)
    rates = []

    for pr in prandtls:
        g.prandtl_number_function = constant(pr)

        rates.append(g.regression_rate)

    plt.plot(prandtls, np.asarray(rates) * 1000)
    plt.title("Regression rate versus Constant Prandtl Number")
    plt.xlabel("Prandtl Number")
    plt.ylabel("Regression Rate [mm/s]")
    plt.show()

def display_viscosity():
    """
    Display the effect that the viscosity of the combustion products has on the regression rate. 
    I believe it only affects the reynolds number of the flow, but that has some impact on the ultimate rate.
    """
    g = new_grain()
    # Viscosity of some kind of Gox HTPB mixture was 1.37e-4
    viscosities = np.linspace(4e-5, 13.7e-5)
    rates = []

    for v in viscosities:
        g.oxidizer_dynamic_viscosity_function = constant(v)

        rates.append(g.regression_rate)

    plt.plot(viscosities * 1e6, np.asarray(rates) * 1000)
    plt.title("Regression rate versus Constant Viscosities")
    # FIXME: units are wrong
    plt.xlabel("Viscosities [Pa/s * e-6]")
    plt.ylabel("Regression Rate [mm/s]")
    plt.show()

def display_latent_heat():
    """
    Display the effect that the latent heat of vaporization of the fuel grain has on the regression rate. The number is very difficult to determine and depends highly on the differing makeup of composites.
    """
    g = new_grain()
    # My only data point is that paraffin is 1.8e6
    heats = np.linspace(1e5, 1e7)
    rates = []

    for h in heats:
        g.latent_heat_function = constant(h)

        rates.append(g.regression_rate)

    plt.plot(heats, np.asarray(rates) * 1000)
    plt.title("Regression rate versus Constant Latent Heat")
    plt.xlabel("Latent Heats [MJ/kg]")
    plt.ylabel("Regression Rate [mm/s]")
    plt.show()


def display_length():
    g = new_grain()
    g.verbose = True
    lengths = np.linspace(0.1, 2.5)
    rates = []

    for l in lengths:
        g.length = l

        rates.append(g.regression_rate)

    plt.plot(lengths, np.asarray(rates) * 1000)
    plt.title("Regression rate versus Length")
    plt.xlabel("Length [m]")
    plt.ylabel("Regression Rate [mm/s]")
    plt.show()

def display_temperature():
    g = new_grain()
    temperatures = np.linspace(500, 3000) # Kelvin
    rates = []

    for t in temperatures:
        g.update_regression(3, 0, t)

        rates.append(g.regression_rate)

    plt.plot(temperatures, np.asarray(rates) * 1000)
    plt.title("Regression rate versus Temperature")
    plt.xlabel("Temperature [K]")
    plt.ylabel("Regression Rate [mm/s]")
    plt.show()

if __name__ == "__main__":

    # display_prandtl()
    display_viscosity()
    # display_temperature()
    # display_latent_heat()
    
    # display_length()

    pass