import matplotlib.pyplot as plt
import numpy as np


def find_efficiencies(cea_object, chamber_pressure=360, area_ratio=4, OFs=np.linspace(2, 18, 200)):
    cstars = []
    specific_impulses = []

    for OF in OFs:
        # convert from ft/s to m/s
        cstar = cea_object.get_Cstar(chamber_pressure, OF) * 0.3048
        cstars.append(cstar)

        specific_impulses.append(cea_object.estimate_Ambient_Isp(chamber_pressure, OF, eps=area_ratio)[0])

    return cstars, specific_impulses, OFs

def display_OF_graph(cea_object, chamber_pressure=360, area_ratio=4):
    cstars, specific_impulses, OFs = find_efficiencies(cea_object, chamber_pressure, area_ratio)
    
    def optimal_input(inputs, outputs):
        return inputs[outputs.index(max(outputs))]

    best_cstar = optimal_input(OFs, cstars)
    best_impulse = optimal_input(OFs, specific_impulses)

    print(f"The optimal OF ratio according to c* is {best_cstar}, giving {max(cstars)} m/s")
    print(f"The optimal OF ratio according to specific impulse is {best_impulse}, giving {max(specific_impulses)} seconds")

    fig, ax1 = plt.subplots()

    ax1.plot(OFs, cstars, label="C*")

    ax2 = ax1.twinx()

    ax2.plot(OFs, specific_impulses, color="red", label="I_sp")

    fig.legend()

    plt.show()
