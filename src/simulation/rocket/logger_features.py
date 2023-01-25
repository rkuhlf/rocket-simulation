from lib.units import Units
from lib.logging.logger import Feature, feature_time

feature_z_position = Feature("z position", "rocket.position.z", Units.m)
feature_x_position = Feature("x position", "rocket.position.x", Units.m)
feature_y_position = Feature("y position", "rocket.position.y", Units.m)

feature_z_force = Feature("z net force", "rocket.force.z", Units.N)
feature_x_force = Feature("x net force", "rocket.force.x", Units.N)
feature_y_force = Feature("y net force", "rocket.force.y", Units.N)

feature_z_drag = Feature("z drag", "rocket.drag.z", Units.N)
feature_x_drag = Feature("x drag", "rocket.drag.x", Units.N)
feature_y_drag = Feature("y drag", "rocket.drag.y", Units.N)

feature_z_lift = Feature("z lift", "rocket.lift.z", Units.N)
feature_x_lift = Feature("x lift", "rocket.lift.x", Units.N)
feature_y_lift = Feature("y lift", "rocket.lift.y", Units.N)

feature_z_velocity = Feature("z velocity", "rocket.velocity.z", Units.mps)
feature_x_velocity = Feature("x velocity", "rocket.velocity.x", Units.mps)
feature_y_velocity = Feature("y velocity", "rocket.velocity.y", Units.mps)

feature_z_acceleration = Feature("z acceleration", "rocket.acceleration.z", Units.mps2)
feature_x_acceleration = Feature("x acceleration", "rocket.acceleration.x", Units.mps2)
feature_y_acceleration = Feature("y acceleration", "rocket.acceleration.y", Units.mps2)

# add one for net force

# Add one for lift
feature_AOA = Feature("AOA", "rocket.angle_of_attack", Units.radians)
feature_heading_around = Feature("heading", "rocket.target_heading.around", Units.radians)
feature_heading_down = Feature("heading", "rocket.target_heading.down", Units.radians)

feature_theta_around = Feature("theta around", "rocket.rotation.around", Units.radians)
feature_theta_down = Feature("theta down", "rocket.rotation.down", Units.radians)

feature_omega_around = Feature("omega around", "rocket.angular_velocity.around", Units.rps)
feature_omega_down = Feature("omega down", "rocket.angular_velocity.down", Units.rps)

feature_alpha_around = Feature("alpha around", "rocket.angular_acceleration.around", Units.rps2)
feature_alpha_down = Feature("alpha down", "rocket.angular_acceleration.down", Units.rps2)


feature_mass = Feature("mass", "rocket.total_mass", Units.kg)

feature_thrust = Feature("thrust", "rocket.thrust", Units.N)

feature_CD = Feature("CD", "rocket.CD", Units.amount)
feature_CL = Feature("CL", "rocket.CL", Units.amount)

feature_stability_cals = Feature("stability", "rocket.stability_cals", Units.cals)
feature_stability_lengths = Feature("stability", "rocket.stability_lengths", Units.m)

base_features = set([feature_time, feature_z_position, feature_x_position, feature_y_position, feature_z_velocity, feature_x_velocity, feature_y_velocity, feature_z_acceleration, feature_x_acceleration, feature_y_acceleration, feature_theta_around, feature_theta_down, feature_omega_around, feature_omega_down, feature_alpha_around, feature_alpha_down])

extended_features = base_features.union([feature_z_position, feature_x_position, feature_y_position, feature_z_force, feature_x_force, feature_y_force, feature_z_drag, feature_x_drag, feature_y_drag, feature_z_lift, feature_x_lift, feature_y_lift, feature_z_velocity, feature_x_velocity, feature_y_velocity, feature_z_acceleration, feature_x_acceleration, feature_y_acceleration, feature_AOA, feature_heading_around, feature_heading_down, feature_theta_around, feature_theta_down, feature_omega_around, feature_omega_down, feature_alpha_around, feature_alpha_down, feature_mass, feature_thrust, feature_CD, feature_CL, feature_stability_cals, feature_stability_lengths])