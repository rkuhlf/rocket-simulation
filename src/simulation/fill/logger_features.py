from lib.units import Units
from lib.logger import Feature, feature_time

feature_fill_tank_pressure = Feature("fill pressure", "fill_tank.pressure", Units.Pa)



base_features = set([feature_fill_tank_pressure])