# LOOP OVER OFs CONSIDERING DIFFERENT INPUTS
# At the moment, we don't have a lot of information about our combustion chamber pressure, so the amount of stuff we can actually implement is limited
# TODO: in the future, I should consider output temperature. The temperature of the propellant should partially determine what chamber pressure we equalize at, which has had a significant effect on the specific impulse (higher is better).

# CONCLUSIONS
# Changing the propellant temperature does literally nothing. That is slightly concerning
# Area ratio of the nozzle has a significant effect on optimal O/F once you start to get to space, and a small effect for us. The bigger the expansion the more oxidizer you want (for us)
# Pressure does not really have a significant effect for us. As the pressure increases by 150 psi, the O/F goes up by about 0.1
# If you have a ton of contamination with sulfur dioxide, that will cause the optimal O/F to increase by a ton (10% gives a 0.8 increase)
# Similarly, for every percent contamination you have, the Isp decreases by one
# However, both of these effects are minimal below 2%
# Contamination by nitrogen also has a limited effect. It does even less than the sulfur, but it looks like it moves the O/F higher faster. If you have 20% contamination, as suggested by a Whitemore paper, that will lower C* by 50-ish m/s 
# The percent of curative has a small effect, shifting the best point down 1 second and over by 0.2 O/F for every 20%
# 5% carbon black drops specific impulse by 1; little effect on O/F. Presumably carbon black is designed to increase regression. It does increase the temperature a teeny bit
# Max Isp for this brand of HTPB in space (eps=40) is right around 270 seconds; based on the lack of effect composition had, I would guess that the formula does not affect all that much
# Overall, pressure and area ratio have a more significant effect on O/F and max Isp than any compositional differences; we want to keep HTPB and nitrous as pure as possible

# Also, ground-level Isp versus space-level Isp makes a huge difference

import numpy as np
import matplotlib.pyplot as plt


from src.data.input.chemistry.PropellantDefinitions import define_HTPB_nitrous
from src.data.manipulation.AnalyzePropellant import display_effect_of_pressure, find_efficiencies, display_OF_graph

htpb_nitrous = None


def save_full_output(name="htpbNitrous.txt"):
    # TODO: not 100% sure what this is doing.
    output = htpb_nitrous.get_full_cea_output(360, 7, 4)

    with open(f"Data/Input/CEAOutput/{name}", "w") as f:
        f.write(output)

    print(output)


def display_effect_of_contamination():
    global htpb_nitrous

    fig, (ax1, ax2) = plt.subplots(1, 2)

    for contamination in np.linspace(0, 15, 16):
        htpb_nitrous = define_HTPB_nitrous(percent_sulfur_contamination=contamination)
        _, impulses, OFs = find_efficiencies()
        
        ax1.plot(OFs, impulses, label=f"{contamination}")

    ax1.set(title="Effect of Sulfur Dioxide Contamination")
    ax1.legend()


    for contamination in np.linspace(0, 15, 16):
        htpb_nitrous = define_HTPB_nitrous(percent_nitrogen_contamination=contamination)
        _, impulses, OFs = find_efficiencies()
        
        ax2.plot(OFs, impulses, label=f"{contamination}")

    ax2.set(title="Effect of Nitrogen Contamination")
    ax2.legend()

    fig.tight_layout()
    plt.show()

def display_effect_of_curative():
    global htpb_nitrous

    fig, ax1 = plt.subplots()

    for curative in np.linspace(0, 60, 10):
        htpb_nitrous = define_HTPB_nitrous(percent_curative=curative)
        _, impulses, OFs = find_efficiencies()
        
        ax1.plot(OFs, impulses, label=f"{curative}")

    ax1.set(title="Effect of Curative on Efficiency")

    fig.legend()
    plt.show()

def display_effect_of_carbon_black():
    global htpb_nitrous

    fig, ax1 = plt.subplots()

    for carbon_black in np.linspace(0, 30, 10):
        htpb_nitrous = define_HTPB_nitrous(percent_carbon_black=carbon_black)
        _, impulses, OFs = find_efficiencies()
        
        ax1.plot(OFs, impulses, label=f"{carbon_black}")

    ax1.set(title="Effect of Carbon Black on Efficiency")

    fig.legend()
    plt.show()



if __name__ == "__main__":
    htpb_nitrous = define_HTPB_nitrous(percent_sulfur_contamination=5)
    # save_full_output()
    # display_effect_of_contamination()
    # display_effect_of_curative()
    # display_effect_of_carbon_black()

    # k = define_HTPB_nitrous()
    # display_OF_graph(k)

    display_effect_of_pressure(htpb_nitrous, pressures=np.linspace(100, 10000, 10), best_possible=True)
    pass


