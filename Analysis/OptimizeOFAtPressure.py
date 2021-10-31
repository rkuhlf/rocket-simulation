# LOOP OVER OFs, DETERMINE THE BEST
# At the moment, we don't have a lot of information about our combustion chamber pressure, so the amount of stuff we can actually implement is limited
# Assuming 25 bar and area ratio of


import numpy as np
import matplotlib.pyplot as plt
from rocketcea.cea_obj import CEA_Obj, add_new_fuel, add_new_oxidizer, add_new_propellant

# by default, it has the HTPB and N2O at 76-ish F. This is probably fine for the HTPB, we will see what effecti it has to change it
paraffin_nitrous = CEA_Obj(oxName="N2O", fuelName="HTPB")


# I am assuming 25 bar = 360 psi. I wish I could do something better, but I don't have any information on how the chamber pressure changes over time
chamber_pressure = 360 # psi

# It is actually pretty fast
# OFs = np.linspace(0.1, 30, 500)
OFs = [6.93]
cstars = []
specific_impulses = []

for OF in OFs:
    # convert from ft/s to m/s
    cstar = paraffin_nitrous.get_Cstar(chamber_pressure, OF) * 0.3048
    cstars.append(cstar)

    specific_impulses.append(paraffin_nitrous.get_Isp(chamber_pressure, OF, eps=5.7))
    print(paraffin_nitrous.get_Throat_MolWt_gamma(chamber_pressure, OF, eps=5.7))
    print(paraffin_nitrous.get_full_cea_output(chamber_pressure, OF, eps=5.7))
    # print(cstar)


def optimal_input(inputs, outputs):
    return inputs[outputs.index(max(outputs))]

best_cstar = optimal_input(OFs, cstars)
best_impulse = optimal_input(OFs, specific_impulses)

print(f"The optimal OF ratio according to c* is {best_cstar}")
print(f"The optimal OF ratio according to specific impulse is {best_impulse}")

fig, ax1 = plt.subplots()

ax1.plot(OFs, cstars, label="C*")

ax2 = ax1.twinx()

ax2.plot(OFs, specific_impulses, color="red", label="I_sp")

fig.legend()

plt.show()

