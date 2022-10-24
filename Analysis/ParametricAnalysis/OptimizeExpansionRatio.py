# DETERMINE OPTIMAL EPS FOR NOZZLE
# Quick script to run the CEA for whatever nozzle



from Data.Input.CEA.CEAPropellants import define_ABS_nitrous
from RocketParts.Motor.nozzle import determine_expansion_ratio as determine_eps_constant_gamma


combustion_chamber_pressure = 362 # psia
external_pressure = 13.053396 # psia

combo_to_sim = define_ABS_nitrous()

# print(combo_to_sim.estimate_Ambient_Isp())
print(combo_to_sim.get_eps_at_PcOvPe(Pc=combustion_chamber_pressure, MR=6.18, PcOvPe=combustion_chamber_pressure / external_pressure))

# This optimal is extremely sensitive to the gamma. This ratio has a square root effect on the gamma, but I do not think that will shrink the impact of poorly calculated gamma
# Fortunately, composition of ABS has relatively little effect on the optimal eps
print(determine_eps_constant_gamma(combustion_chamber_pressure, external_pressure, 1.17))