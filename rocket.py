import numpy as np

from Helpers.general import euler_to_vector_2d, angle_from_vector_2d

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


from Helpers.thrust import *
from Helpers.general import interpolate

# also includes any libraries that are imported in this file
from preset_object import PresetObject

# Have a separate motor class

# Have a separate parachute class

# Have a separate fin class?


class Rocket(PresetObject):

    def __init__(
            self, config={},
            environment=None, motor=None, parachute=None, logger=None):
        self.position = np.array([0, 0], dtype="float64")
        self.velocity = np.array([0, 0], dtype="float64")
        self.acceleration = np.array([0, 0], dtype="float64")


        # Using Euler X, Y, Z angles instead of quaternions because I am not a psychopath
        # Only need one dimension of rotation for two dimensions of position
        # When third dimension is added change it to three - this may cause some hard angle problems converting directional velocities to angular velocities in three dimensions
        self.rotation = np.array([np.pi / 2], dtype="float64")
        self.angular_velocity = np.array([0], dtype="float64")
        self.angular_acceleration = np.array([0], dtype="float64")

        # This is just the mass of the frame, the motor and propellant will be added in a second
        self.mass = 1.86  # kg

        self.radius = 0.05  # meters
        self.height = 4  # meters
        # TODO: get approximate position of motor so that I can recalculate center of gravity every frame
        self.center_of_gravity = 2  # meters from the bottom
        self.center_of_pressure = 0.8  # meters from the bottom



        # Calculate using http://www.rasaero.com/dl_software_ii.htm
        # TODO: figure out a way to simulate this so that it works in 3D
        # Probably the theoretical best thing to do is to calculate the drag coefficient of the object rotated so that the relative velocity is only in one dimension. Calculating separate drag coefficients for two components of velocity doesn't make sense, so it is necessary to rotate the shape so that it is at the same angle against a one component velocity, find the consequent drag force, then combine that to the unrotated force
        self.drag_coefficient = 0.75
        self.drag_coefficient_perpendicular = 1.08

        self.vertical_area = np.pi * self.radius ** 2  # 0.008  # m^2
        self.sideways_area = self.radius * 2 * self.height  # 0.4 m^2


        super().overwrite_defaults(config)

        self.motor = motor
        self.environment = environment
        self.parachute = parachute
        self.logger = logger



        self.update_previous()


        # TODO: Double check if I am supposed to be adding the propellant mass to the rocket mass to match tanner's model (what should the total weight of the rocket actually be)
        self.mass += self.motor.mass


        # Indicates whether the rocket has begun to descend
        self.turned = False
        self.landed = False
        self.dist_gravity_pressure = self.center_of_gravity - self.center_of_pressure

    def update_previous(self):
        """Update the variables that hold last frame's rocket features"""
        self.p_position = np.copy(self.position)  # p stands for previous
        self.p_velocity = np.copy(self.velocity)
        self.p_acceleration = np.copy(self.acceleration)

        self.p_rotation = np.copy(self.rotation)
        self.p_angular_velocity = np.copy(self.angular_velocity)
        self.p_angular_acceleration = np.copy(self.angular_acceleration)

    def get_drag_torque(self, drag_coefficient):
        altitude = self.environment.base_altitude + self.position[1]

        air_density = self.environment.get_air_density(altitude)

        # Might need this later for getting drag_coefficient better
        # renold = air_density * area * drag_coefficient / 2

        # just totally ignore frictional angular drag
        # and use the equation CD * pi * h * density * Angular velocity ^ 2 * radius ^ 4
        # The coefficient of drag is the same as for linear drag
        drag_force = drag_coefficient * np.pi * self.height * \
            air_density * (self.angular_velocity ** 2) * self.radius ** 4

        # In the same direction, so wen we subtract it the velocity will decrease
        drag_torque = drag_force * np.sign(self.angular_velocity)

        return drag_torque

    def calculate_torque(self, force):
        # The drag force fully applies to the translational motion of the rocket, but it also fully applies to the rotational momentum of the object
        # calculate the angle between the vector application and the 'lever arm,' which is the rocket body in this case
        # In 3d, torque will be in 3 dimensions as well, complicating rotation
        torque = 0
        if not np.all(force == 0):
            # It oscillates on the descent - I feel like this should be fixable with a few negative signs
            # Would a rocket without a parachute rotate like that?
            # Should be really close to 0 degrees
            angle = angle_from_vector_2d(force) - self.rotation

            self.logger.add_items({"Angle to Body": angle})


            # basically just gives the component that will have an affect on the rocket, the opposite of the opposite / hypotenuse (magnitude of vector)
            perpendicular_component = np.linalg.norm(
                force) * np.sin(angle)

            torque += self.dist_gravity_pressure * perpendicular_component

        # This rotation drag is always in the opposite direction of angular velocity. Be aware that that isn't always the same as the direction of torque due to translation
        # It is in te 10 ^ -4 range. That seems like it is too low to cause the rotation to converge
        rotation_drag = self.get_drag_torque(
            self.drag_coefficient_perpendicular)

        # I think that the angular drag is probably also applied at the center of pressure
        torque -= rotation_drag * self.dist_gravity_pressure


        return torque


    def get_drag_force(self, area, drag_coefficient):
        # Assumes the same area and drag coefficient for flight upward and downward
        altitude = self.get_altitude()


        air_density = self.environment.get_air_density(altitude)
        renold = air_density * area * drag_coefficient / 2

        # FIXME: maybe should be the other way around
        relative_velocity = self.velocity - self.environment.get_air_speed()

        magnitude = np.linalg.norm(relative_velocity)
        if np.isclose(magnitude, 0):
            return np.array([0, 0])

        unit_direction = relative_velocity / magnitude


        # You can't square each component of velocity and have it be in the same direction
        # So, multiply by the magnitude of the square, as the formula intends, then by the unit direction
        air_resistance = renold * (magnitude ** 2)


        # In the same direction, so wen we subtract it later the velocity will decrease
        air_resistance *= unit_direction


        return air_resistance

    def calculate_force(self):
        # Forces don't carry over from frame to frame, so we need to set them back to zero
        # All of the force causes full translation
        total_force = np.array([0., 0.])
        # Only some of the force is applied off center, causing rotation
        rotating_force = np.array([0., 0.])

        total_force[1] -= self.environment.get_gravitational_attraction(
            self.mass, self.position[1])


        # This will have to change. Need to get the new area and the drag coefficient at run time
        # This function only adjusts for the air density at altitude and the velocity of the rocket
        # Just using vertical area right now. TODO: implement area calculations to get the cross sectional area of a rotated object
        drag_force = self.get_drag_force(
            self.vertical_area, self.drag_coefficient)

        total_force -= drag_force

        # changing this to a minus sign here, will have to change some other stuff when the sim starts
        rotating_force -= drag_force



        # Should really be doing angle adjustments before thrust, but sometimes life doesn't happen, and it causes negligable problems
        thrust = self.motor.get_thrust(self.environment.time)
        # thrust is in direction of the rotation

        unit_direction = euler_to_vector_2d(self.rotation)
        directed_thrust = np.reshape(thrust * unit_direction, (2,))

        # nan
        total_force += directed_thrust


        new_mass = self.mass - self.motor.thrust_to_mass(
            thrust, self.environment.time_increment)

        # adjust for conservation of momentum
        self.velocity *= self.mass / new_mass


        self.mass = new_mass


        return total_force, rotating_force


    def combine(self, a, b):
        """Returns the average of a and b"""
        # Taking the average of the current acceleration and the previous acceleration is a better approximation of the change over the time_interval
        # It is basically a riemann midpoint integral over the acceleration so that it is more accurate finding the change in velocity
        return (a + b) / 2

    def apply_angular_acceleration(self):
        combined_angular_acceleration = self.combine(
            self.p_angular_acceleration, self.angular_acceleration)
        self.angular_velocity += combined_angular_acceleration * self.environment.time_increment

        combined_angular_velocity = self.combine(
            self.p_angular_velocity, self.angular_velocity)
        self.rotation += combined_angular_velocity * self.environment.time_increment

    def apply_acceleration(self):
        combined_acceleration = self.combine(
            self.p_acceleration, self.acceleration)
        self.velocity += combined_acceleration * self.environment.time_increment

        combined_velocity = self.combine(self.p_velocity, self.velocity)
        self.position += combined_velocity * self.environment.time_increment


    def simulate_step(self):
        self.logger.add_items({'time': self.environment.time})

        total_force, rotating_force = self.calculate_force()
        torque = self.calculate_torque(rotating_force)


        # FIXME: Actually this sucks and is complicated because moment of inertia isn't a scalar quantity for a complex 3d shape
        # use calculated value from Fusion 360/Other CAD, currently using random one
        moment_of_inertia = 1 / 12 * self.mass * self.height ** 2


        self.angular_acceleration = torque / moment_of_inertia
        self.apply_angular_acceleration()

        self.acceleration = total_force / self.mass
        self.apply_acceleration()


        if self.position[1] <= 0:
            self.landed = True

        if self.position[1] < self.p_position[1]:
            self.turned = True

            # Deploy parachute here

        self.update_previous()




    def get_altitude(self):
        return self.environment.base_altitude + self.position[1]
