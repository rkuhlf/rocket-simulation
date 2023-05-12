from lib.units import Units
from lib.logging.logger import Feature, feature_time

feature_fill_tank_pressure = Feature("fill pressure", "fill_tank.pressure", Units.Pa)
feature_run_tank_pressure = Feature("run pressure", "run_tank.pressure", Units.Pa)
feature_head_loss = Feature("head loss", "p_head_loss", Units.Pa)

feature_run_tank_mass = Feature("run mass", "run_tank.ox_mass", Units.kg)
feature_fill_tank_mass = Feature("fill mass", "fill_tank.ox_mass", Units.kg)

feature_fill_tank_temperature = Feature("fill temperature", "fill_tank.temperature", Units.K)
feature_run_tank_temperature = Feature("run temperature", "run_tank.temperature", Units.K)

feature_flow_rate = Feature("flow rate", "p_flow_rate", Units.kg)



base_features = set([feature_fill_tank_pressure, feature_run_tank_pressure, feature_run_tank_mass, feature_fill_tank_mass, feature_flow_rate, feature_head_loss, feature_fill_tank_temperature, feature_run_tank_temperature])