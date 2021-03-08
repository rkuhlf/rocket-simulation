

# TODO: Refactor te program to be more object oriented. There should be a rocket class, of which you can create an instance, then run the simulation. That class should accept an instance of a motor class, and it should accept an instance of a parachute class.

# TODO: add parachute logic
# When the velocity flips
# Change drag coefficient
# Change area

# TODO: account better for drift
# Account for air resistance of rocket shape
# TODO: Add the affect of wind

""" TODO: six degree of freedom - in x, y, and z modelling
Model rotation in x, y, and z
Figure out how to determine the change in motion and the change in rotation from a push not exactly at the center of mass
"""

# TODO: Expand on and implement unit tests

# All of these import * are really bad practice. They clutter the interpreter (making it run slower), and they make it hard for linters to detect undefined names
# However, I think it is fine atm for testing stuff
from Helpers.dragForce import *
from Helpers.gravity import *
from Helpers.thrust import *
from Helpers.general import interpolate

# also includes any libraries that are imported in this file
from Helpers.variables import *

p_position = np.copy(position)  # p stands for previous
p_velocity = np.copy(velocity)
p_acceleration = np.copy(acceleration)

p_rotation = np.copy(rotation)
p_angular_velocity = np.copy(angular_velocity)
p_angular_acceleration = np.copy(angular_acceleration)


# Tanner's model currently reaces apogee at 3158 meters
# My model reaches 4081
# The difference is probably due to drag_coefficient implementation and momentum calculations




# Calculate using http://www.rasaero.com/dl_software_ii.htm
# TODO: figure out a way to simulate this so that it works in 3D
# Probably the theoretical best thing to do is to calculate the drag coefficient of the object rotated so that the relative velocity is only in one dimension. Calculating separate drag coefficients for two components of velocity doesn't make sense, so it is necessary to rotate the shape so that it is at the same angle against a one component velocity, find the consequent drag force, then combine that to the unrotated force
drag_coefficient = 0.75
drag_coefficient_perpendicular = 1.08

vertical_area = np.pi * radius ** 2  # 0.008  # m^2
sideways_area = radius * 2 * height  # 0.4 m^2
area = np.array([sideways_area, vertical_area])


to_log = {}


def simulate_step():
    # acceleration has to be global so that it can be logged
    global t, mass, velocity, position, acceleration, rotation, angular_velocity, angular_acceleration

    t += time_increment

    # You have to reset acceleration every time
    force = np.array([0., 0.])

    # Account for gravity decreasing as you leave the atmosphere
    force[1] -= get_gravitational_attraction()


    # This will have to change. Need to get the new area and the drag coefficient at run time
    # This function only adjusts for the air density at altitude and the velocity of the rocket
    # Just using vertical area right now. TODO: implement area calculations to get the cross sectional area of a rotated object
    drag_force = get_drag_force(vertical_area, drag_coefficient)

    force -= drag_force



    # The drag force fully applies to the translational motion of the rocket, but it also fully applies to the rotational momentum of the object
    # torque = drag_force * distance between center of pressure and center of gravity
    # returns 3d vector, so I have to convert it into that rotation
    # calculate the angle between the vector application and the 'lever arm,' which is the rocket body in this case
    # simple for 2d
    torque = 0
    if not np.all(drag_force == 0):
        # It oscillates on the descent - I feel like this should be fixable with a few negative signs
        # Would a rocket without a parachute rotate like that?
        # Should be really close to 0 degrees
        angle = angle_from_vector_2d(drag_force) - rotation

        # if (velocity[1] < 0.5):
        #     print("Drag angle", drag_force, angle_from_vector_2d(drag_force))
        #     print("Drag angle to body", angle)

        to_log['Drag to Body'] = angle


        # basically just gives the component that will have an affect on the rocket, the opposite of the opposite / hypotenuse (magnitude of vector)
        perpendicular_component = np.linalg.norm(drag_force) * np.sin(angle)

        torque += dist_gravity_pressure * perpendicular_component

    # This rotation drag is always in the opposite direction of angular velocity. Be aware that that isn't always the same as the direction of torque due to translation
    # It is in te 10 ^ -4 range. That seems like it is too low to cause the rotation to converge
    rotation_drag = get_drag_torque(drag_coefficient_perpendicular)

    # I think that the angular drag is probably also applied at the center of pressure
    torque -= rotation_drag * dist_gravity_pressure


    # Do all angle stuff first, since some of it affects how forces are applied

    # Actually this sucks and is complicated because moment of inertia isn't a scalar quantity for a complex 3d shape
    # use calculated value from Fusion 360/Other CAD, currently using random one
    moment_of_inertia = 1 / 12 * mass * height ** 2


    # FIXME: Moment of inertia needs to update every frame since mass changes
    angular_acceleration = torque / moment_of_inertia

    combined_angular_acceleration = (
        p_angular_acceleration + angular_acceleration) / 2
    angular_velocity += combined_angular_acceleration * time_increment

    combined_angular_velocity = (p_angular_velocity + angular_velocity) / 2
    rotation += combined_angular_velocity * time_increment


    # thrust is in direction of the rotation
    thrust = get_thrust(t - time_increment / 2)
    unit_direction = euler_to_vector_2d(rotation)
    # adjust this for the angle


    directed_thrust = np.reshape(thrust * unit_direction, (2,))
    # directed_thrust = np.array([0, thrust]) # This is the old bad way

    # Thrust is working in the correct direction
    force += directed_thrust

    new_mass = mass - thrust * mass_per_thrust * time_increment
    # adjust for momentum
    velocity *= mass / new_mass


    mass = new_mass

    acceleration = force / mass

    # Taking the average of the current acceleration and the previous acceleration is a better approximation of the change over the time_interval
    # It is basically a riemann midpoint integral over the acceleration so that it is more accurate finding the change in velocity
    combined_acceleration = (
        p_acceleration + acceleration) / 2
    velocity += acceleration * time_increment

    combined_velocity = (p_velocity + velocity) / 2
    position += combined_velocity * time_increment


rows = []
print("Launching rocket")

while position[1] >= 0:
    to_log = {}

    simulate_step()

    # y is the second index
    if not turned and position[1] < p_position[1]:
        print('Reached the turning point at %.3s seconds with a height of %.5s meters' % (
            t, position[1]))
        turned = True

    # Making copies of things is slow but I don't really have a choice
    # Actually, it is a little better to just use te indexes
    to_log.update({
        'time': t,
        'position': position.copy(),
        'velocity': velocity.copy(),
        'acceleration': acceleration,
        'rotation': rotation.copy(),
        'angular velocity': angular_velocity.copy(),
        'angular acceleration': angular_acceleration
    })

    rows.append(to_log)

    p_position = np.copy(position)
    p_velocity = np.copy(velocity)
    p_acceleration = np.copy(acceleration)

    p_rotation = np.copy(rotation)
    p_angular_velocity = np.copy(angular_velocity)
    p_angular_acceleration = np.copy(angular_acceleration)

print(
    "Rocket landed with a speed of %.3s m/s after %.4s seconds of flight time." %
    (np.linalg.norm(velocity),
     t))

# This stuff adds about two seconds to the run time
df = pd.DataFrame(rows)
df.set_index('time', inplace=True)

df.to_csv("Data/Output/output.csv")

print("Saved the trial to csv")
