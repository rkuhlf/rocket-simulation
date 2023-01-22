# DEFINITIONS FOR VARIOUS PROPELLANTS TO RUN CEA WITH
# It is nice to have custom functions that way I can iterate over very specific properties



from numpy.core import overrides
from rocketcea.cea_obj import add_new_fuel, add_new_oxidizer
from rocketcea.cea_obj_w_units import CEA_Obj
from rocketcea import cea_obj 


units = {
    "isp_units": 'sec',
    "cstar_units": 'm/sec',
    "pressure_units": 'bar',
    "temperature_units": 'K',
    "sonic_velocity_units": 'm/sec',
    "enthalpy_units": 'J/kg',
    "density_units": 'kg/m^3',
    "specific_heat_units": 'J/kg-K',
    "viscosity_units": 'millipoise',
    "thermal_cond_units": 'W/cm-degC'
}


def define_nitrous_card(percent_sulfur_contamination=0, percent_nitrogen_contamination=0, temperature=298.15):
    card_str = f"""
    oxid NitrousOxide  N 2.0 O 1.0  wt%={100 - percent_sulfur_contamination - percent_nitrogen_contamination}
    h,cal=19497.759 t(k)={temperature}
    oxid SulfurDioxide S 1.0 O 2.0 wt%={percent_sulfur_contamination}
    h,cal=-70946 t(k)={temperature}
    oxid Nitrogen N 2.0 wt%={percent_nitrogen_contamination}
    h,cal=0 t(k)={temperature}
    """
    add_new_oxidizer('ContaminatedNitrous', card_str)

    return card_str

def define_HTPB_card(percent_curative, percent_carbon_black, fuel_temperature):
    card_str = f"""
    fuel HTPB   C 0.662 H 1.0 O 0.00662    wt%={(100 - percent_curative) * (100 - percent_carbon_black) / 100}
    h,cal=-271.96 t(k)={fuel_temperature}
    fuel Curative  C 224 H 155 O 27 N 27  wt%={percent_curative * (100 - percent_carbon_black) / 100}
    h,cal=-738686.932 t(k)={fuel_temperature}
    fuel CarbonBlack C 1 wt%={percent_carbon_black}
    h,cal=0 t(k)={fuel_temperature}
    """

    add_new_fuel('MixedHTPB', card_str)


def define_HTPB_nitrous(percent_sulfur_contamination=0, percent_nitrogen_contamination=0, percent_curative=17, percent_carbon_black=3, oxidizer_temperature = 298.15, fuel_temperature=298.15, overrides_units=False):
    # Notice that all of these custom cards require the enthalpy in cal/mol
    # Sulfur Dioxide can apparently contaminate the nitrous up to 2% mass, so we should take a look at the differences
    
    define_nitrous_card(percent_sulfur_contamination, percent_nitrogen_contamination, oxidizer_temperature)
    define_HTPB_card(percent_curative, percent_carbon_black, fuel_temperature)

    cea_obj._CacheObjDict = {}

    if overrides_units:
        return CEA_Obj(oxName="ContaminatedNitrous", fuelName="MixedHTPB", **units)

    return CEA_Obj(oxName="ContaminatedNitrous", fuelName="MixedHTPB")


def define_ABS_nitrous(percent_sulfur_contamination=0, percent_nitrogen_contamination=0, percent_acrylonitrile=40, percent_butadiene=47, percent_styrene=13, oxidizer_temperature=298.15, fuel_temperature=298.15, overrides_units=False):
    # Notice that all of these custom cards require the enthalpy in cal/mol
    # Sulfur Dioxide can apparently contaminate the nitrous up to 2% mass, so we should take a look at the differences
    
    define_nitrous_card(percent_sulfur_contamination, percent_nitrogen_contamination, oxidizer_temperature)
    
    card_str = f"""
    fuel Acrylonitrile   C 3 H 3 N 1    wt%={percent_acrylonitrile}
    h,cal=3927 t(k)={fuel_temperature}
    fuel Butadiene  C 4 H 6  wt%={percent_butadiene}
    h,cal=26112 t(k)={fuel_temperature}
    fuel Styrene C 8 H 8 wt%={percent_styrene}
    h,cal=31560 t(k)={fuel_temperature}
    """

    add_new_fuel('ABS', card_str)

    cea_obj._CacheObjDict = {}
    
    if overrides_units:
        return CEA_Obj(oxName="ContaminatedNitrous", fuelName="ABS", **units)

    return CEA_Obj(oxName="ContaminatedNitrous", fuelName="ABS")


def get_cal_per_mole(calories_per_gram, molar_mass):
    "Accepts a specific enthalpy in calories per gram along with a molar mass and converts it into calories per mole"
    # Propep DAF file is in cal/gram

    return calories_per_gram * molar_mass

def get_hydrocarbon_molar_mass(carbons, hydrogens, oxygens, nitrogens=0):
    return carbons * 12.011 + hydrogens * 1.008 + oxygens * 15.999 + nitrogens * 14.007


if __name__ == "__main__":
    # print(get_cal_per_mole(74, get_hydrocarbon_molar_mass(3, 3, 0, 1)))
    define_HTPB_card(17, 3, 298.15)
    output = CEA_Obj(oxName="GOX", fuelName="MixedHTPB")

    print(output.get_Temperatures(Pc=360, MR=2, eps=5))

    pass