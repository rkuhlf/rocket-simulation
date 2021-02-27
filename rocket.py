# TODO: add parachute logic
# When the velocity flips
# Change drag coefficient
# Change area
# TODO: account better for drift
# Account for air resistance of rocket shape
# TODO: three degree of freedom - in x, y, and z modelling
# Model rotation in x, y, and z

from Helpers.dragForce import *
from Helpers.gravity import *
from Helpers.thrust import *
from Helpers.general import interpolate

# also includes any libraries that are imported in this file
from Helpers.variables import *

p_position = np.copy(position)  # p stands for previous
p_velocity = np.copy(velocity)
p_acceleration = np.copy(acceleration)


# Tanner's model currently reaces apogee at 3158 meters
# My model reaches 3400


def simulate_step():
    # acceleration has to be global so that it can be logged
    global t, mass, velocity, position, acceleration

    t += time_increment

    # You have to reset acceleration every time
    force = np.array([0., 0.])

    # Account for gravity decreasing as you leave the atmosphere
    force[1] -= get_gravitational_attraction()


    thrust = get_thrust(t - time_increment / 2)
    # adjust this for the angle
    force[1] += thrust

    new_mass = mass - thrust * mass_per_thrust * time_increment
    # adjust for momentum
    velocity *= mass / new_mass


    mass = new_mass


    # This will have to change. Need to get the new area and the drag coefficient at run time
    # This function only adjusts for the air density at altitude and the velocity of the rocket
    force -= get_drag_force(area, drag_coefficient)

    acceleration = force / mass


    # Taking the average of the current acceleration and the previous acceleration is a better approximation of the change over the time_interval
    # It is basically a riemann midpoint integral over the acceleration so that it is more accurate finding the change in velocity
    combined_acceleration = (
        p_acceleration + acceleration) / 2
    velocity += acceleration * time_increment

    combined_velocity = (p_velocity + velocity) / 2
    position += combined_velocity * time_increment


# Calculate using http://www.rasaero.com/dl_software_ii.htm
drag_coefficient = 0.75  # double check that it would be the same both up and sideways
# TODO: Find real data for areas
vertical_area = 0.008  # m^2
sideways_area = 0.1  # m^2
area = np.array([sideways_area, vertical_area])


rows = []
print("Launching rocket")

while position[1] >= 0:
    simulate_step()

    # y is the second index
    if not turned and position[1] < p_position[1]:
        print('Reached the turning point at %.3s seconds with a height of %.5s meters' % (
            t, position[1]))
        turned = True

    # Making copies of things is slow but I don't really have a choice
    # Actually, it is a little better to just use te indexes
    to_log = {
        'time': t,
        'position': position[1],
        'acceleration': acceleration
    }

    rows.append(to_log)

    p_position = np.copy(position)
    p_velocity = np.copy(velocity)
    p_acceleration = np.copy(acceleration)

print(
    "Rocket landed with a speed of %.3s m/s after %.4s seconds of flight time." %
    (np.linalg.norm(velocity),
     t))

# This stuff adds about two seconds to the run time
df = pd.DataFrame(rows)

df.to_csv("Data/Output/output.csv")
