import numpy as np
from Helpers.general import euler_to_vector_2d, angle_from_vector_2d, combine



# TODO: account better for drift
# Account for air resistance of rocket shape
# TODO: Add the affect of wind

""" TODO: six degree of freedom - in x, y, and z modelling
Model rotation in x, y, and z
Figure out how to determine the change in motion and the change in rotation from a push not exactly at the center of mass
"""

# TODO: Check that I'm using horizontal area where appropriate


from Helpers.general import interpolate

# also includes any libraries that are imported in this file
from preset_object import PresetObject

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
        # The simulation works unless you start with  diff rotation
        # When rotation is zero (measured in radians), the rocket is headed straight up
        self.rotation = np.array([0], dtype="float64")
        self.angular_velocity = np.array([0], dtype="float64")
        self.angular_acceleration = np.array([0], dtype="float64")

        # This is just the mass of the frame, the motor and propellant will be added in a second
        self.mass = 1.86  # kg

        self.radius = 0.05  # meters
        self.height = 4  # meters
        # TODO: get approximate position of motor so that I can recalculate center of gravity every frame
        # It should be do-able with only the initial center of gravity (and mass), and the position of the motor and the mass that is lost
        # This is actually a relatively large difference, but hopefully increasing it will slow down rotation
        self.center_of_gravity = 2  # meters from the bottom
        self.center_of_pressure = 0.8  # meters from the bottom



        # Calculate using http://www.rasaero.com/dl_software_ii.htm
        # TODO: figure out a way to simulate this so that it works in 3D
        # Probably the theoretical best thing to do is to calculate the drag coefficient of the object rotated so that the relative velocity is only in one dimension. Calculating separate drag coefficients for two components of velocity doesn't make sense, so it is necessary to rotate the shape so that it is at the same angle against a one component velocity, find the consequent drag force, then combine that to the unrotated force
        self.drag_coefficient = 0.75
        self.drag_coefficient_perpendicular = 1.08

        self.vertical_area = np.pi * self.radius ** 2  # 0.008  # m^2
        self.sideways_area = self.radius * 2 * self.height  # 0.4 m^2

        # This is overriden in the simulation initialization
        self.apply_angular_forces = False

        self.motor = motor
        self.environment = environment
        self.parachute = parachute
        self.logger = logger

        # Everything before this is saved as a preset
        super().overwrite_defaults(config)


        self.update_previous()


        # maybe should make an addmotor method
        self.mass += self.motor.mass
        self.mass += self.parachute.mass


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
        "Calculate the magnitude of the force opposed to the direction of rotation"
        # Angular drag is a completely different calculation from translational drag

        air_density = self.environment.get_air_density(self.get_altitude())

        # Might need this later for getting drag_coefficient better
        # renold = air_density * area * drag_coefficient / 2

        # just totally ignore shear angular drag and use the equation CD * pi * h * density * Angular velocity ^ 2 * radius ^ 4 from https://physics.stackexchange.com/questions/304742/angular-drag-on-body
        # TODO: Check when shear stress is important (possibly for very thin rockets?)
        # The coefficient of drag is the same as for linear drag atm, probably not realistic
        drag_torque = drag_coefficient * np.pi * self.height * \
            air_density * (self.angular_velocity ** 2) * self.radius ** 4

        # In the same direction, so when we subtract it the velocity will decrease
        drag_torque *= np.sign(self.angular_velocity)

        return drag_torque

    def calculate_torque(self, force):
        "Calculate the torque caused by an arbitrary force"
        # The drag force fully applies to the translational motion of the rocket, but it also fully applies to the rotational momentum of the object
        # calculate the angle between the vector application and the 'lever arm,' which is the rocket body in this case
        # In 3d, torque will be in 3 dimensions as well, complicating rotation
        torque = 0
        if not np.all(force == 0):
            # Should be really close to 0 or pi, especially right at the start
            # TODO: Figure out why tf I need this
            force[0] *= -1
            angle = angle_from_vector_2d(-force) - self.rotation - np.pi / 2

            self.logger.add_items({"Angle to Body": angle})


            # basically just gives the component that will have an affect on the rocket, the opposite of the opposite / hypotenuse (magnitude of vector)
            perpendicular_component = np.linalg.norm(
                force) * np.sin(angle)

            # TODO: Check sign
            torque += self.dist_gravity_pressure * perpendicular_component
            self.logger.add_items(
                {"Translational component of angular drag": torque.copy()})


        # This rotation drag is always in the opposite direction of angular velocity. Be aware that that isn't always the same as the direction of torque due to translation
        # It is in the 10 ^ -4 range. That seems like it is too low to cause the rotation to converge
        rotation_drag = self.get_drag_torque(
            self.drag_coefficient_perpendicular) * 10000



        # No multiplication by dist_grav_press. If center of mass and center of pressure were identical, the object would still experience angular drag
        # It is subtracted from the eventual torque because get_drag_torque is calculated in the direction of rotation
        torque -= rotation_drag
        self.logger.add_items(
            {"Angular component of angular drag": -rotation_drag.copy()})


        return torque


    def get_drag_force(self, area, drag_coefficient):
        "Calculate the magnitude of the translational drag force"

        air_density = self.environment.get_air_density(self.get_altitude())
        renold = air_density * area * drag_coefficient / 2

        # FIXME: maybe should be the other way around
        relative_velocity = self.velocity - self.environment.get_air_speed()

        magnitude = np.linalg.norm(relative_velocity)
        # TODO: figure out why tf this is here
        if np.isclose(magnitude, 0):
            return np.array([0, 0])

        unit_direction = relative_velocity / magnitude


        # You can't square each component of velocity and have it be in the same direction
        # So, multiply by the magnitude of the square, as the formula intends, then by the unit direction
        air_resistance = renold * (magnitude ** 2)


        # In the same direction, so wen we subtract it later the velocity will decrease
        air_resistance *= unit_direction


        return air_resistance

    def calculate_forces(self):
        # Forces don't carry over from frame to frame, so we need to set them back to zero
        # The full force is applied in the fector direction that it has
        total_force = np.array([0., 0.])
        # Only the perpendicular component is applied to the rotation
        rotating_force = np.array([0., 0.])

        # There is a constant gravitational force downwards
        total_force[1] -= self.environment.get_gravitational_attraction(
            self.mass, self.get_altitude())


        # This will have to change. Need to get the new area and the drag coefficient at run time
        # This function only adjusts for the air density at altitude and the velocity of the rocket
        # Just using vertical area right now.
        # TODO: implement area calculations to get the cross sectional area of a rotated object
        drag_force = self.get_drag_force(
            self.vertical_area, self.drag_coefficient)

        total_force -= drag_force

        # I think this is the problem - I'm pretty sure not all of the energy of the air is applied to rotating the rocket. It is inelastic-ish, but I think that ish plays a big enough role that you can't just assume it's 100%. I'm not even sure if the word inelastic applies
        # changing this to a minus sign here, will have to change some other stuff when the sim starts
        # It should be something like rotating_force -= drag_force * 0.5, but I can't figure out what
        # TODO: See if a plus works here
        rotating_force -= drag_force  # Force eventually added to the velocity
        self.logger.add_items(
            {"Direction of translational drag": rotating_force.copy()})



        thrust = self.motor.get_thrust(self.environment.time)

        # thrust is in direction of the rotation. The larger the angle is, the more to the right the rocket is
        unit_direction = euler_to_vector_2d(np.pi / 2 - self.rotation)
        directed_thrust = np.reshape(thrust * unit_direction, (2,))


        total_force += directed_thrust


        new_mass = self.mass - self.motor.thrust_to_mass(
            thrust, self.environment.time_increment)

        # adjust for conservation of momentum
        self.velocity *= self.mass / new_mass
        self.mass = new_mass


        return total_force, rotating_force


    def apply_angular_acceleration(self):
        combined_angular_acceleration = combine(
            self.p_angular_acceleration, self.angular_acceleration)
        self.angular_velocity += combined_angular_acceleration * self.environment.time_increment

        if (self.apply_angular_forces):
            combined_angular_velocity = combine(
                self.p_angular_velocity, self.angular_velocity)

            self.rotation += combined_angular_velocity * self.environment.time_increment

    def apply_acceleration(self):
        combined_acceleration = combine(
            self.p_acceleration, self.acceleration)
        self.velocity += combined_acceleration * self.environment.time_increment

        combined_velocity = combine(self.p_velocity, self.velocity)
        self.position += combined_velocity * self.environment.time_increment


    def simulate_step(self):
        self.logger.add_items({'time': self.environment.time})

        total_force, rotating_force = self.calculate_forces()
        torque = self.calculate_torque(rotating_force)


        # FIXME: Actually this sucks and is complicated because moment of inertia isn't a scalar quantity for a complex 3d shape
        # use calculated value from Fusion 360/Other CAD, currently using random one for a cylinder
        moment_of_inertia = 1 / 12 * self.mass * self.height ** 2


        self.angular_acceleration = torque / moment_of_inertia
        self.apply_angular_acceleration()

        self.acceleration = total_force / self.mass
        self.apply_acceleration()


        if self.position[1] <= self.environment.base_altitude:
            self.landed = True

        if self.position[1] < self.p_position[1]:
            self.turned = True

            # TODO: Figure out how parachute deployment mechanisms tend to work. Is it always as soon as it turns? How long does it take? Calculate the forces on the parachute chord
            # self.parachute.deploy(self)

        self.update_previous()


    def get_altitude(self):
        return self.environment.base_altitude + self.position[1]
