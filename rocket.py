# There are a few main areas that need improvement
# There is no variable center of gravity. This is relatively easy to fix and will play a large role in stability
# There is no variable center of pressure. This is much harder to fix. I can get a crappy solution from Rasaero, but I would really like to use CFD data
# The CL & CD don't work past four degrees. This is just further impetus to get verifiable CFD data. Until that point I can't really move forwards here.

import numpy as np
from Helpers.general import vector_from_angle, angle_between, combine, magnitude, angled_cylinder_cross_section
# from Helpers.fluidSimulation import cutout_method, barrowman_equation, extended_barrowman_equation
from Data.Input.models import get_coefficient_of_drag, get_coefficient_of_lift


# TODO: Factor in changing center of gravity
# TODO: get approximate position of motor so that I can recalculate center of gravity every frame
# It should be do-able with only the initial center of gravity (and mass), and the position of the motor and the mass that is lost



from Helpers.general import interpolate, project

# also includes any libraries that are imported in this file
from preset_object import PresetObject



class Rocket(PresetObject):

    # Torque is in radians per second-squared * kg

    def __init__(
            self, config={},
            environment=None, motor=None, parachute=None, logger=None):
        # X, Y, Z values, where Z is upwards
        self.position = np.array([0, 0, 0], dtype="float64")
        self.velocity = np.array([0, 0, 0], dtype="float64")
        self.acceleration = np.array([0, 0, 0], dtype="float64")

        self.rotation = np.array(
            [np.pi / 2, -0.05],
            dtype="float64")
        self.angular_velocity = np.array([0, 0], dtype="float64")
        self.angular_acceleration = np.array([0, 0], dtype="float64")

        # This is just the mass of the frame, the motor and propellant will be added in a second
        self.mass = 1.86  # kg

        self.radius = 0.05  # meters
        self.height = 2  # meters

        self.reference_area = np.pi * self.radius ** 2  # 0.008  # m^2

        # region Set References
        self.motor = motor
        self.environment = environment
        self.parachute = parachute
        self.logger = logger
        # endregion

        super().overwrite_defaults(config)
        # Everything before this is saved as a preset including whatever is overridden by config

        # This is overriden in the simulation initialization, so it is just here as a reminder
        self.apply_angular_forces = True

        self.calculate_cached()

        self.update_previous()

        # TODO: Test the refactor and see if bestangle by wind still works (mit need a reset() metod)

        # maybe should make an addmotor method
        self.mass += self.motor.mass
        self.mass += self.parachute.mass

        # Indicates whether the rocket has begun to descend
        self.turned = False
        self.landed = False

        self.force = np.array([0., 0., 0.])
        self.torque = np.array([0., 0.])

    def simulate_step(self):
        self.calculate_cached()
        if self.logger is not None:
            self.logger.add_items({'time': self.environment.time})


        # First, apply all of the forces to the rocket
        self.apply_air_resistance()
        self.apply_thrust()
        self.apply_gravity()

        # Then, update the object's position and speed
        self.apply_acceleration()
        self.apply_velocity()

        if (self.apply_angular_forces):
            self.apply_angular_acceleration()
            self.apply_angular_velocity()


        # Has anything changed since the last frame
        if self.position[2] < 0:
            self.landed = True

        if self.position[2] < self.p_position[2]:
            self.turned = True

            # TODO: Figure out how parachute deployment mechanisms tend to work. Is it always as soon as it turns? How long does it take? Calculate the forces on the parachute chord
            # self.parachute.deploy(self)


        # Set yourself up for the next frame
        self.update_previous()
        self.force = np.array([0., 0., 0.])
        self.torque = np.array([0., 0.])



    # region UPDATING KINEMATICS


    def apply_velocity(self):
        combined_velocity = combine(self.p_velocity, self.velocity)
        self.position += combined_velocity * self.environment.time_increment

    def apply_acceleration(self):
        combined_acceleration = combine(
            self.p_acceleration, self.get_acceleration())
        self.velocity += combined_acceleration * self.environment.time_increment

    def get_acceleration(self):
        self.acceleration = self.force / self.mass
        return self.force / self.mass


    def apply_angular_velocity(self):
        combined_angular_velocity = combine(
            self.p_angular_velocity, self.angular_velocity)
        self.rotation += combined_angular_velocity * self.environment.time_increment

    def apply_angular_acceleration(self):
        combined_angular_acceleration = combine(
            self.p_angular_acceleration, self.get_angular_acceleration())
        self.angular_velocity += combined_angular_acceleration * self.environment.time_increment


        # Flip all of the rotation
        # Change the theta_down
        # Swap te velocity so tat it is still oin te same way
        if (self.rotation[1] > np.pi):
            self.rotation[0] += np.pi
            self.rotation[0] %= np.pi * 2
            overshoot = self.rotation[1] - np.pi
            # basically just 360 - rotation down
            self.rotation[1] = np.pi - overshoot

            self.angular_acceleration[1] *= -1
            self.angular_velocity[1] *= -1
            self.logger.add_items({"flipped": 1})
        elif (self.rotation[1] < 0):
            # Should just turn this into a function, want to make sure it's identical
            self.rotation[0] += np.pi
            self.rotation[0] %= np.pi * 2

            self.rotation[1] = -self.rotation[1]

            self.angular_acceleration[1] *= -1
            self.angular_velocity[1] *= -1
            self.logger.add_items({"flipped": 1})
        else:
            self.logger.add_items({"flipped": 0})

    def get_angular_acceleration(self):
        self.angular_acceleration = self.torque / self.moment_of_inertia
        return self.torque / self.moment_of_inertia



    def update_previous(self):
        """Update the variables that hold last frame's rocket features"""
        self.p_position = np.copy(self.position)  # p stands for previous
        self.p_velocity = np.copy(self.velocity)
        self.p_acceleration = np.copy(self.acceleration)

        self.p_rotation = np.copy(self.rotation)
        self.p_angular_velocity = np.copy(self.angular_velocity)
        self.p_angular_acceleration = np.copy(self.angular_acceleration)

    # endregion

    # region FORCE BASED CALCULATIONS


    def apply_force(
            self, value, direction, distance_from_nose=None, debug=False,
            name="Force"):
        # Where direction is a unit vector
        if distance_from_nose is None:
            distance_from_nose = self.CG

        if debug:
            self.logger.add_items(
                {name: value * direction})

        self.force += value * direction

        distance_from_CG = distance_from_nose - self.CG

        self.apply_torque(value, direction, distance_from_CG)

    def apply_torque(self, value, direction, distance_from_CG):
        # Figure out how the force * the distance affects each direction of rotation
        # Calculate the torque caused by an arbitrary force
        # The drag force fully applies to the translational motion of the rocket, but it also fully applies to the rotational momentum of the object
        # calculate the torque in two perpendicular directions
        # Perpendicular is slightly more complicated in 3D. We need the component of the force that is perpendicular to the current rotation of the rocket. To me, it seems like the easiest thing is to break the force down into each of it's components and calculate that individually
        z_component = direction[2] * value
        # The z component cannot cause rotation around, only affecting theta down
        z_component_perpendicular = z_component * \
            np.sin(self.theta_down())
        # When rocket is completely horizontal (90 degrees), it should apply 100%, when vertical, 0%. This is sine.

        # a torque in the vertical direction (positive z component), should cause an increase in theta down
        self.torque[1] += distance_from_CG * z_component_perpendicular



        x_component = direction[0] * value
        # The around rotation determines what fraction of the force goes to the yaw and what fraction to the torque. When the rocket hasn't spun at all, all of the x_component goes to the pitch
        # I might just need the value of this
        pitch_multiplier = np.cos(self.theta_around())
        # If the rocket was travelling horizontally, there wouldn't be any force. 90 -> 0
        angle_of_incidence_multiplier = np.cos(self.theta_down())

        self.torque[1] -= x_component * pitch_multiplier * \
            angle_of_incidence_multiplier * distance_from_CG


        # Only apply the leftover x to the yaw
        yaw_multiplier = np.sin(self.theta_around())
        # When the rocket is horizontal, however, the yaw will still be fully applied. I don't think I need any other multiplier

        self.torque[0] += x_component * yaw_multiplier * distance_from_CG

        y_component = direction[1] * value
        pitch_multiplier = np.sin(self.theta_around())
        angle_of_incidence_multiplier = np.cos(self.theta_down())

        self.torque[1] -= y_component * pitch_multiplier * \
            angle_of_incidence_multiplier * distance_from_CG


        yaw_multiplier = np.cos(self.theta_around())
        # x and y can't cause yaw in the same direction (I think, so we'll just have them be opposite)
        self.torque[0] -= y_component * yaw_multiplier * distance_from_CG

        # self.logger.add_items(
        #   {"Yaw torque after y translational drag": torque[0].copy()})



    def apply_air_resistance(self):
        # Translational drag
        if not np.isclose(self.dynamic_pressure, 0):
            drag_magnitude, drag_direction, lift_magnitude, lift_direction = self.get_translational_drag()
            self.apply_force(drag_magnitude, drag_direction,
                             self.CP, debug=True, name="Drag")
            self.apply_force(lift_magnitude, lift_direction,
                             self.CP, debug=True, name="Lift")

        # Angular drag
        if not np.all(np.isclose(self.angular_velocity, 0)):
            pass

    def get_translational_drag(self):
        "Calculate the vector for the translational drag force"
        # The nomenclature here can be very confusing

        drag = self.dynamic_pressure * self.reference_area * self.CD
        lift = self.dynamic_pressure * self.reference_area * self.CL

        relative_velocity = self.velocity - \
            self.environment.get_air_speed(self.get_altitude())

        # Drag force is applied in the same direction as freestream velocity
        drag_direction = - relative_velocity / magnitude(relative_velocity)

        # Lift force is applied perpendicular to the freestream velocity
        # This is the part that is stupid because I should just use normal and axial forces
        # Assumin lift forces are in te same plane as dra forces and te rocket (if it was defined as a line)
        # Tis isnt perfectly accurate, but it is impossible to do better witout more detailed information from Rasaero

        heading = vector_from_angle(self.rotation)
        component_in_drag_direction = project(heading, drag_direction)

        lift_direction = heading - component_in_drag_direction
        lift_direction /= magnitude(lift_direction)


        return drag, drag_direction, lift, lift_direction


    def get_angular_drag(self):
        # This affects a very small component of the overall flight

        pass


    def apply_thrust(self):
        thrust = self.motor.get_thrust(self.environment.time)

        new_mass = self.mass - self.motor.thrust_to_mass(
            thrust, self.environment.time_increment)

        self.mass = new_mass

        # thrust is in direction of the rotation. The larger the angle is, the more to the right the rocket is
        self.apply_force(thrust, vector_from_angle(self.rotation))


    def apply_gravity(self):

        gravity = self.environment.get_gravitational_attraction(
            self.mass, self.get_altitude())

        self.apply_force(
            gravity, np.array([0, 0, -1]),
            debug=True, name="Gravity")

    # endregion

    # region GENERAL FUNCTIONS

    def theta_around(self):
        return self.rotation[0]

    def theta_down(self):
        return self.rotation[1]

    def get_mach(self):
        # How many speed of sounds am I going
        v = self.environment.get_speed_of_sound(self.get_altitude())

        return magnitude(self.velocity) / v

    def get_altitude(self):
        # Using Z as up vector
        return self.environment.base_altitude + self.position[2]

    # region Cached Values

    def calculate_dynamic_pressure(self):
        relative_velocity = self.velocity - \
            self.environment.get_air_speed(self.get_altitude())

        self.dynamic_pressure = 1 / 2 * self.environment.get_air_density(
            self.get_altitude()) * magnitude(
            relative_velocity) ** 2

    def calculate_angle_of_attack(self):
        relative_velocity = self.velocity - \
            self.environment.get_air_speed(self.get_altitude())

        self.angle_of_attack = angle_between(
            relative_velocity, vector_from_angle(self.rotation))

    def calculate_moment_of_inertia(self):
        # FIXME: Actually this sucks and is complicated because moment of inertia isn't a scalar quantity for a complex 3d shape
        # use calculated value from Fusion 360/Other CAD, currently using random one for a cylinder
        self.moment_of_inertia = 1 / 12 * self.mass * self.height ** 2

    def calculate_coefficient_of_drag(self):
        self.CD = get_coefficient_of_drag(
            self.get_mach(), self.angle_of_attack)

    def calculate_coefficient_of_lift(self):
        self.CL = get_coefficient_of_lift(
            self.get_mach(), self.angle_of_attack)

    def calculate_center_of_pressure(self):
        self.CP = 1.8
        # cutout = cutout_method()
        # barrowman = barrowman_equation()

        # self.center_of_pressure = extended_barrowman_equation(
        #     self.get_angle_of_attack(), barrowman, cutout)

    def calculate_center_of_gravity(self):
        self.CG = 1.0

    def calculate_cp_cg_dist(self):
        # Note that this is only used for dynamic stability calculations, nothing during the simulations
        self.dist_press_grav = self.CP - self.CG

    def calculate_cached(self):
        self.calculate_dynamic_pressure()
        self.calculate_angle_of_attack()
        self.calculate_moment_of_inertia()
        self.calculate_coefficient_of_drag()
        self.calculate_coefficient_of_lift()
        self.calculate_center_of_pressure()
        self.calculate_center_of_gravity()
        self.calculate_cp_cg_dist()

    # endregion
    # endregion


    # TODO: Add tis back in better
    # def get_drag_torque(self, drag_coefficient):
    #     "Calculate the magnitude of the force opposed to the direction of rotation"
    #     # Angular drag is a completely different calculation from translational drag

    #     air_density = self.environment.get_air_density(self.get_altitude())

    #     # Some of the radius multiplications come from converting angular velocity to tangent velocity
    #     # just totally ignore shear angular drag and use the equation CD * pi * h * density * Angular velocity ^ 2 * radius ^ 4 from https://physics.stackexchange.com/questions/304742/angular-drag-on-body
    #     # TODO: Check when shear stress is important (possibly for very thin rockets?)

    #     # This radius is wrong. Should be the radius of the rotating circle?
    #     # TODO: Fix the radius
    #     drag_around = drag_coefficient * np.pi * self.height * air_density * \
    #         (self.angular_velocity[0] ** 2) * self.radius ** 4
    #     drag_down = drag_coefficient * np.pi * self.height * air_density * \
    #         (self.angular_velocity[1] ** 2) * self.radius ** 4

    #     # should be opposite the direction of motion
    #     if np.sign(self.angular_velocity[0]) == np.sign(drag_around):
    #         drag_around *= -1
    #     if np.sign(self.angular_velocity[1]) == np.sign(drag_down):
    #         drag_down *= -1


    #     return drag_around, drag_down

    # def calculate_torque(self, force):

    #     # ANGULAR DRAG APPLICATION
    #     # This should definitely be a different function. What if I want to have separate calls to find translational torque
    #     # This rotation drag is always in the opposite direction of angular velocity. Be aware that that isn't always the same as the direction of torque due to translation
    #     # It is in the 10 ^ -4 range. That seems like it is too low to cause the rotation to converge
    #     # The impulse that this supplies should never be bigger than the impulse that the rocket is rotating with. TODO: Figure out how to calculate the momentum of rotation an object has (mv -> moment of inertia * rotational velocity)
    #     # TODO: Check if dist_rav_press is correct ere
    #     current_rotational_momentum = self.moment_of_inertia * \
    #         self.angular_velocity * self.dist_gravity_pressure

    #     # Thoug it isn't exactly great design, I think that around drag should use drag_coefficient_perpendicular and down_drag should also use the perpendicular. This is an approximation
    #     around_drag, down_drag = self.get_drag_torque(
    #         self.drag_coefficient_perpendicular)

    #     # FIXME: this is not how it works anymore. Rather than applying a force opposite the angle, we need to make sure three components are pointing the opposite way. Somehow I need to figure out if it is overdoing it in any direction TODO: Add back in

    #     def more_than_cancels(initial, change):
    #         return abs(change) > abs(initial) and np.sign(change) != np.sign(
    #             initial)

    #     if more_than_cancels(
    #             current_rotational_momentum[0],
    #             around_drag * self.environment.time_increment):
    #         # This actually has an effect a significant portion of the time
    #         around_drag = current_rotational_momentum[0] / \
    #             self.environment.time_increment

    #     if more_than_cancels(
    #             current_rotational_momentum[1],
    #             down_drag * self.environment.time_increment):
    #         # This actually has an effect a significant portion of the time
    #         down_drag = current_rotational_momentum[1] / \
    #             self.environment.time_increment


    #     # This is making almost zero difference
    #     # No multiplication by dist_grav_press. If center of mass and center of pressure were identical, the object would still experience angular drag
    #     torque[0] += around_drag
    #     torque[1] += down_drag

    #     return torque
