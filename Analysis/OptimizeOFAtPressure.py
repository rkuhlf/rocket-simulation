# LOOP OVER OFs, DETERMINE THE BEST
# At the moment, we don't have a lot of information about our combustion chamber pressure, so the amount of stuff we can actually implement is limited
# Assuming 25 bar and figuring out the area ratio

# CONCLUSIONS
# Changing the propellant temperature does literally nothing. That is slightly concerning
# Area ratio of the nozzle has a significant effect on optimal O/F once you start to get to space, and a small effect for us. The bigger the expansion the more oxidizer you want (for us)
# Pressure does not really have a significant effect for us. As the pressure increases by 150 psi, the O/F goes up by about 0.1
# If you have a ton of contamination with sulfur dioxide, that will cause the optimal O/F to increase by a ton (10% gives a 0.8 increase)
# Similarly, for every percent contamination you have, the Isp decreases by one
# However, both of these effects are minimal below 2%
# The percent of curative has a small effect, shifting the best point down 1 second and over by 0.2 O/F for every 20%
# 5% carbon black drops specific impulse by 1; little effect on O/F. Presumably carbon black is designed to increase regression. It does increase the temperature a teeny bit
# Max Isp for this brand of HTPB is right around 270 seconds; based on the lack of effect composition had, I would guess that the formula does not affect all that much
# Overall, pressure and area ratio have a more significant effect on O/F and max Isp than any compositional differences; we want to keep HTPB and nitrous as pure as possible


import numpy as np
import matplotlib.pyplot as plt
from rocketcea.cea_obj import CEA_Obj, add_new_fuel, add_new_oxidizer
from rocketcea import cea_obj

def define_inputs(percent_contamination=0, percent_curative=17, percent_carbon_black=3, oxidizer_temperature = 298.15, fuel_temperature=298.15):
    global htpb_nitrous

    # Notice that all of these custom cards require the enthalpy in cal/mol
    # Sulfur Dioxide can apparently contaminate the nitrous up to 2% mass, so we should take a look at the differences
    card_str = f"""
    oxid NitrousOxide  N 2.0 O 1.0  wt%={100 - percent_contamination}
    h,cal=19497.759 t(k)={oxidizer_temperature}
    oxid SulfurDioxide S 1.0 O 2.0 wt%={percent_contamination}
    h,cal=-70946 t(k)={oxidizer_temperature}
    """
    add_new_oxidizer('ContaminatedNitrous', card_str)

    card_str = f"""
    fuel HTPB   C 0.662 H 1.0 O 0.00662    wt%={(100 - percent_curative) * (100 - percent_carbon_black) / 100}
    h,cal=-271.96 t(k)={fuel_temperature}
    fuel Curative  C 224 H 155 O 27 N 27  wt%={percent_curative * (100 - percent_carbon_black) / 100}
    h,cal=-738686.932 t(k)={fuel_temperature}
    fuel CarbonBlack C 1 wt%={percent_carbon_black}
    h,cal=0 t(k)={fuel_temperature}
    """

    add_new_fuel('MixedHTPB', card_str)

    cea_obj._CacheObjDict = {}

    htpb_nitrous = CEA_Obj(oxName="ContaminatedNitrous", fuelName="MixedHTPB")


def get_cal_per_mole(calories_per_gram, molar_mass):
    "Accepts a specific enthalpy in calories per gram along with a molar mass and converts it into calories per mole"
    # Propep DAF file is in cal/gram

    return calories_per_gram * molar_mass

def get_hydrocarbon_molar_mass(carbons, hydrogens, oxygens):
    return carbons * 12.011 + hydrogens * 1.008 + oxygens * 15.999

def save_full_output(name="test.txt"):
    output = htpb_nitrous.get_full_cea_output(360, 7, 4)

    with open(f"Data/Input/CEAOutput/{name}", "w") as f:
        f.write(output)

    print(output)


def find_efficiencies(chamber_pressure=360, area_ratio=4, OFs=np.linspace(2, 18, 200)):
    # It is actually pretty fast
    # OFs = [6.93]
    cstars = []
    specific_impulses = []

    for OF in OFs:
        # convert from ft/s to m/s
        cstar = htpb_nitrous.get_Cstar(chamber_pressure, OF) * 0.3048
        cstars.append(cstar)

        specific_impulses.append(htpb_nitrous.get_Isp(chamber_pressure, OF, eps=area_ratio))

        # save_full_output(str(random.uniform()))

    return cstars, specific_impulses, OFs

def display_OF_graph(chamber_pressure=360, area_ratio=4):
    cstars, specific_impulses, OFs = find_efficiencies(chamber_pressure, area_ratio)
    
    def optimal_input(inputs, outputs):
        return inputs[outputs.index(max(outputs))]

    best_cstar = optimal_input(OFs, cstars)
    best_impulse = optimal_input(OFs, specific_impulses)

    print(f"The optimal OF ratio according to c* is {best_cstar}")
    print(f"The optimal OF ratio according to specific impulse is {best_impulse}, giving {max(specific_impulses)} seconds")

    fig, ax1 = plt.subplots()

    ax1.plot(OFs, cstars, label="C*")

    ax2 = ax1.twinx()

    ax2.plot(OFs, specific_impulses, color="red", label="I_sp")

    fig.legend()

    plt.show()


def display_effect_of_contamination():
    fig, ax1 = plt.subplots()

    for contamination in np.linspace(0, 15, 16):
        define_inputs(percent_contamination=contamination)
        _, impulses, OFs = find_efficiencies()
        
        ax1.plot(OFs, impulses, label=f"{contamination}")

    fig.legend()
    plt.show()

def display_effect_of_curative():
    fig, ax1 = plt.subplots()

    for curative in np.linspace(0, 60, 10):
        define_inputs(percent_curative=curative)
        _, impulses, OFs = find_efficiencies()
        
        ax1.plot(OFs, impulses, label=f"{curative}")

    ax1.set(title="Effect of Curative on Efficiency")

    fig.legend()
    plt.show()

def display_effect_of_carbon_black():
    fig, ax1 = plt.subplots()

    for carbon_black in np.linspace(0, 30, 10):
        define_inputs(percent_carbon_black=carbon_black)
        _, impulses, OFs = find_efficiencies()
        
        ax1.plot(OFs, impulses, label=f"{carbon_black}")

    ax1.set(title="Effect of Carbon Black on Efficiency")

    fig.legend()
    plt.show()

def display_effect_of_pressure(pressures=np.linspace(100, 1000, 10), best_possible=False):
    if best_possible:
        define_inputs(percent_carbon_black=0, percent_contamination=0, percent_curative=0)
    else:
        define_inputs()

    fig, ax1 = plt.subplots()

    for pressure in pressures:
        _, impulses, OFs = find_efficiencies(chamber_pressure=pressure)
        
        ax1.plot(OFs, impulses, label=f"{pressure}")

    ax1.set(title="Effect of Pressure on Efficiency")

    fig.legend()
    plt.show()


if __name__ == "__main__":
    # display_effect_of_contamination()
    # display_effect_of_curative()
    # display_effect_of_carbon_black()

    # display_effect_of_pressure(pressures=np.linspace(100, 10000, 50), best_possible=True)

    pass


