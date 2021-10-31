# ROCKET OBJECT
# Simulates the flight of a rocket as a rigidbody in five degrees of freedom - three positional coordinates, two rotational coordinates
# Uses a separate motor class for thrust, and an array of parachutes
# Uses RASAero for looking up various aerodynamic qualities

# here is my plan: 
# Scale it up to the current rocket we are using in class
# Add variable mass and center of gravity from custom things.


# There are a few main areas that need improvement
# There is no variable center of gravity. This is relatively easy to fix and will play a large role in stability
# There is no variable center of pressure. This is much harder to fix. I can get a crappy solution from Rasaero, but I would really like to use CFD data
# The CL & CD don't work past four degrees. This is just further impetus to get verifiable CFD data. Until that point I can't really move forwards here.

import numpy as np
from math import isnan

from Helpers.general import interpolate, project, combine
from Helpers.general import angles_from_vector_3d, vector_from_angle, angle_between, magnitude
from RocketParts.massObject import MassObject
from environment import Environment
from Data.Input.models import get_coefficient_of_drag, get_coefficient_of_lift



class Rocket(MassObject):
    """
        Class that holds all of the aerodynamic calculations for a rocket and very little else
        Most important function is simulate_step; used in the simulation class and is the main entry point
        Avoid modifying the original position values, there may be unexpected consequences. If you need to change the launch altitude, do it from the Environment class
        Feel free to change the starting rotation - it is basically your launch angle.
        Also, everything is in radians.
    """

    # Torque is in radians per second-squared * kg
    def __init__(
            self, config={},
            environment:Environment=None , motor=None, parachutes=[], logger=None):
        super().__init__(config={})
        # X, Y, Z values, where Z is upwards
        self.position = np.array([0, 0, 0], dtype="float64")
        self.velocity = np.array([0, 0, 0], dtype="float64")
        self.acceleration = np.array([0, 0, 0], dtype="float64")

        self.rotation = np.array(
            [np.pi / 2, 0.05],
            dtype="float64")
        self.angular_velocity = np.array([0, 0], dtype="float64")
        self.angular_acceleration = np.array([0, 0], dtype="float64")

        # This is just the mass of the frame, the motor and propellant will be added in a second
        self.mass = 0  # kg
        # Excluding the motor and other sub mass objects
        self.center_of_gravity = 4 # m

        self.radius = 0.11 # meters
        self.length = 7 # meters

        self.reference_area = np.pi * self.radius ** 2  # 0.008  # m^2

        #region SET REFERENCES
        self.motor = motor
        self.environment = environment
        self.parachutes = parachutes
        self.logger = logger

        self.mass_objects = [self.motor]
        self.mass_objects.extend(self.parachutes)
        #endregion

        #region DEFAULT MASSES
        nose_cone = MassObject({
            "center_of_gravity": 0.4,
            "mass": 10 # kg
        })
        ox_tank_shell = MassObject({
            "center_of_gravity": 3,
            "mass": 40 # kg
        })
        injector = MassObject({
            "center_of_gravity": 5,
            "mass": 4 # kg
        })
        phenolic = MassObject({
            "center_of_gravity": 6,
            "mass": 16 # kg
        })
        fins = MassObject({
            "center_of_gravity": 6.5,
            "mass": 10
        })
        nozzle = MassObject({
            "center_of_gravity": 7,
            "mass": 15
        })
        avionics_bay = MassObject({
            "center_of_gravity": 7,
            "mass": 10
        })

        self.mass_objects.extend([nose_cone, ox_tank_shell, injector, phenolic, fins, nozzle, avionics_bay])
        #endregion


        super().overwrite_defaults(config)
        # Everything before this is saved as a preset including whatever is overridden by config

        # This is overriden in the simulation initialization, so it is just here as a reminder
        self.apply_angular_forces = True

        self.calculate_cached()
        self.update_previous()


        # Indicates whether the rocket has begun to descend
        self.turned = False
        self.landed = False

        self.force = np.array([0., 0., 0.])
        self.torque = np.array([0., 0.])

    def simulate_step(self):
        self.calculate_cached()
        self.log_data('time', self.environment.time)


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
        # TODO: add some kind of has lifted of thing
        if self.position[2] < 0 and (self.p_position[2] > 0 or self.position[2] < -100):
            if self.position[2] < -100:
                if self.logger is not None:
                    self.logger.save_to_csv()
                raise Exception("Your rocket fell straight into the ground")

            self.landed = True

        if self.position[2] < self.p_position[2] and not self.turned and (self.position[2] > 0 or self.position[2] < -100):
            self.turned = True

            self.apogee = self.p_position.copy()[2]

            # TODO: Figure out how parachute deployment mechanisms tend to work. Is it always as soon as it turns? How long does it take? Calculate the forces on the parachute chord

        if False: #self.environment.time > self.motor.get_burn_time():
            for parachute in self.parachutes:
                if parachute.should_deploy(self):
                    parachute.deploy(self)


        # Set yourself up for the next frame
        if isnan(self.position[2]):
            raise Exception("Everything fell apart. NaN value in altitude")

        self.log_data("Net Force", self.force)

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
        # We only set the self variable here so that it can be logged
        self.acceleration = self.force / self.total_mass
        return self.force / self.total_mass


    def apply_angular_velocity(self):
        combined_angular_velocity = combine(
            self.p_angular_velocity, self.angular_velocity)
        self.rotation += combined_angular_velocity * self.environment.time_increment

        # Flip all of the rotation
        # Change the theta_down so that it is never negative (should always be between 0 and pi)
        # Swap the velocity so that it is still going the same way
        if (self.rotation[1] > np.pi):
            self.rotation[0] += np.pi
            self.rotation[0] %= np.pi * 2
            overshoot = self.rotation[1] - np.pi
            # basically just 360 - rotation down
            self.rotation[1] = np.pi - overshoot

            # Notice that flipping the rotational acceleration is important, even if it has already been applied this frame. Next frame, when we average it, it will basically be zero, showing the flip
            self.angular_acceleration[1] *= -1
            self.angular_velocity[1] *= -1
            self.log_data("flipped", 1)
        elif (self.rotation[1] < 0):
            # Should just turn this into a function, want to make sure it's identical
            self.rotation[0] += np.pi
            self.rotation[0] %= np.pi * 2

            # Make the rotation positive
            self.rotation[1] = -self.rotation[1]

            self.angular_acceleration[1] *= -1
            self.angular_velocity[1] *= -1
            self.log_data("flipped", 1)
        else:
            self.log_data("flipped", 0)

    def apply_angular_acceleration(self):
        combined_angular_acceleration = combine(
            self.p_angular_acceleration, self.get_angular_acceleration())
        self.angular_velocity += combined_angular_acceleration * self.environment.time_increment


    def get_angular_acceleration(self):
        self.angular_acceleration = self.torque / self.total_moment_of_inertia
        return self.torque / self.total_moment_of_inertia



    def update_previous(self):
        """Update the variables that hold last frame's rocket features"""
        # I am just going to start applying a normal force here because this is super annoying. Hopefully nobody is trying to do one second rocket flights.
        if self.environment.time < 1 and self.position[2] < 0:
            # I think this is making it go through the floor
            self.position = np.array([0, 0, 0], dtype="float64")
            self.velocity = np.array([0, 0, 0], dtype="float64")
            self.acceleration = np.array([0, 0, 0], dtype="float64")

        self.log_data("Target Heading", angles_from_vector_3d(self.velocity))

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
            distance_from_nose = self.total_CG

        if debug:
            self.log_data(name, value * direction)

        self.force += value * direction

        distance_from_CG = distance_from_nose - self.total_CG

        self.apply_torque(value, direction, distance_from_CG)

    def apply_torque(self, value, direction, distance_from_CG):
        """
            Figure out how the force * the distance affects each axis of rotation
            Apply the arbitrary force in-place
        """

        # Perpendicular is slightly more complicated in 3D
        # We need the component of force perpendicular to the current rotation 
        # To me, it seems like the easiest thing is to break the force down 
        # into each component calculated individually


        z_component = direction[2] * value
        # When rocket is completely horizontal (90 degrees), it should apply 100%.
        # when vertical, 0%. This is sine.
        z_component_perpendicular = z_component * np.sin(self.theta_down)

        # The z component cannot cause rotation around, it only affects theta down
        # a torque in the vertical direction (z+), should cause an increase in theta down
        self.torque[1] += distance_from_CG * z_component_perpendicular


        x_component = direction[0] * value
        # When the rocket hasn't spun at all, all of the x_component goes to the pitch
        pitch_multiplier = np.cos(self.theta_around)
        # If the rocket was travelling horizontally, there wouldn't be any force. 90 -> 0
        angle_of_incidence_multiplier = np.cos(self.theta_down)

        # The negative sign and pitch multiplier provide the correct rotational direction
        self.torque[1] -= x_component * pitch_multiplier * \
            angle_of_incidence_multiplier * distance_from_CG


        # Only apply the leftover x to the yaw
        yaw_multiplier = np.sin(self.theta_around)
        # When the rocket is horizontal, the yaw will still be fully applied
        # so no angle of incidence component is necessary.
        self.torque[0] += x_component * \
            yaw_multiplier * distance_from_CG


        y_component = direction[1] * value
        # The pitch multiplier shows force around y axis 
        pitch_multiplier = np.sin(self.theta_around)
        angle_of_incidence_multiplier = np.cos(self.theta_down)

        self.torque[1] -= y_component * pitch_multiplier * \
            angle_of_incidence_multiplier * distance_from_CG


        yaw_multiplier = np.cos(self.theta_around)
        # x and y can't cause yaw in the same direction
        self.torque[0] -= y_component * yaw_multiplier * distance_from_CG


    def apply_air_resistance(self):
        # Translational drag
        if not np.isclose(self.dynamic_pressure, 0):
            drag_magnitude, drag_direction, lift_magnitude, lift_direction = self.get_translational_drag()
            self.apply_force(drag_magnitude, drag_direction,
                             self.CP, debug=True, name="Drag")
            self.apply_force(lift_magnitude, lift_direction,
                             self.CP, debug=True, name="Lift")

        # FIXME: Angular drag: not currently implemented
        if not np.all(np.isclose(self.angular_velocity, 0)):
            pass

    def get_translational_drag(self):
        "Calculate the vector for the translational drag force"
        # The nomenclature here can be very confusing

        drag = self.dynamic_pressure * self.reference_area * self.CD
        lift = self.dynamic_pressure * self.reference_area * self.CL

        relative_velocity = self.velocity - \
            self.environment.get_air_speed(self.altitude)


        self.log_data('air speed', self.environment.get_air_speed(
            self.altitude))
        self.log_data('relative velocity', relative_velocity)

        # Drag force is applied in the same direction as freestream velocity
        drag_direction = - relative_velocity / magnitude(relative_velocity)

        # Lift force is applied perpendicular to the freestream velocity
        # This is the part that is stupid because I should just use normal and axial forces
        # Assuming lift forces are in te same plane as drag forces and the rocket (if it was defined as a line)
        heading = vector_from_angle(self.rotation)
        component_in_drag_direction = project(heading, drag_direction)

        lift_direction = heading - component_in_drag_direction

        # I don't know how to explain this, but it took me a solid four hours of debugging to figure out.
        # When the fins are in the air, we still project to the same side, so the sign is wrong
        fins_over_nose = False

        if self.angle_of_attack > np.pi / 2:
            fins_over_nose = True

        if fins_over_nose:
            # If we are pointed the downwards, we should still be restoring the fins downwards (on ascent)
            lift_direction *= -1

        if np.all(np.isclose(lift_direction, 0)):
            lift = 0
            lift_direction = np.array([0, 0, -1])
        else:
            lift_direction /= magnitude(lift_direction)


        return drag, drag_direction, lift, lift_direction


    def get_angular_drag(self):
        # This affects a very small component of the overall flight

        pass


    def apply_thrust(self):
        # Calculate indicates there are side effects, namely, the mass decreases
        thrust = self.motor.calculate_thrust(self.environment.time)

        self.log_data("Thrust", thrust)

        # thrust is in direction of the rotation. The larger the angle is, the more to the right the rocket is
        self.apply_force(thrust, vector_from_angle(self.rotation))


    def apply_gravity(self):

        gravity = self.environment.get_gravitational_attraction(
            self.total_mass, self.altitude)

        self.apply_force(
            gravity, np.array([0, 0, -1]),
            debug=True, name="Gravity")

    # endregion

    # region GENERAL FUNCTIONS
    def log_data(self, name, data):
        if self.logger is not None:
            self.logger.add_items({name: data})

    @property
    def theta_around(self):
        return self.rotation[0]

    @property
    def theta_down(self):
        return self.rotation[1]

    @property
    def mach(self):
        # How many speed of sounds am I going
        v = self.environment.get_speed_of_sound(self.altitude)

        return magnitude(self.velocity) / v

    @property
    def gees(self):
        """
        Return the number of gees the rocket is accelerating at
        Adjusted for the variation as the rocket leaves the atmosphere (because I can)
        """
        grav_acceleration = self.environment.get_gravitational_attraction(self.total_mass, self.altitude) / self.total_mass
        return magnitude(self.acceleration) / grav_acceleration

    @property
    def altitude(self):
        # Using Z as up vector
        return self.environment.base_altitude + self.position[2]

    # region Cached Values

    def calculate_dynamic_pressure(self):
        relative_velocity = self.velocity - \
            self.environment.get_air_speed(self.altitude)

        self.dynamic_pressure = 1 / 2 * self.environment.get_air_density(
            self.altitude) * magnitude(
            relative_velocity) ** 2

    def calculate_angle_of_attack(self):
        relative_velocity = self.velocity - \
            self.environment.get_air_speed(self.altitude)

        self.angle_of_attack = angle_between(
            relative_velocity, vector_from_angle(self.rotation))

        self.log_data("AOA1", self.angle_of_attack)

    # def calculate_moment_of_inertia(self):
    # FIXME: Actually this sucks and is complicated because moment of inertia isn't a scalar quantity for a complex 3d shape. Double actually, I am not even rotating around the center of mass - this calculation rotates around the center of volume.
    # Right now, it is an underestimate, because the masses are closer than they would actually be. Therefore, a usual stability margin will be more unstable than expected in the model
    # use calculated value from Fusion 360/Other CAD, currently using random one for a cylinder
    # self.moment_of_inertia = 1 / 12 * self.mass * self.length ** 2

    def calculate_coefficient_of_drag(self):
        for parachute in self.parachutes:
            if parachute.deployed:
                return
        self.log_data("AOA", self.angle_of_attack)
        
        self.CD = get_coefficient_of_drag(
            self.mach, self.angle_of_attack)
        self.log_data("CD", self.CD)

    def calculate_coefficient_of_lift(self):
        self.CL = get_coefficient_of_lift(
            self.mach, self.angle_of_attack)
        self.log_data("CL", self.CL)


    def calculate_center_of_pressure(self):
        # This should give one caliber of stability
        # FIXME: change back to 5 so the other one works
        self.CP = 3.75 # meters
        # cutout = cutout_method()
        # barrowman = barrowman_equation()

        # self.center_of_pressure = extended_barrowman_equation(
        #     self.get_angle_of_attack(), barrowman, cutout)

    def calculate_cp_cg_dist(self):
        # Note that this is only used for dynamic stability calculations, nothing during the simulations
        self.dist_press_grav = self.CP - self.total_CG
        self.log_data("Stability [Calibers]", self.dist_press_grav / (self.radius * 2))
        self.log_data("Stability [Lengths]", self.dist_press_grav / (self.length))

    def calculate_cached(self):
        self.calculate_dynamic_pressure()
        self.calculate_angle_of_attack()
        self.calculate_coefficient_of_drag()
        self.calculate_coefficient_of_lift()
        self.calculate_center_of_pressure()
        self.calculate_cp_cg_dist()

    # endregion
    # endregion


    # TODO: Add tis back in better
    # def get_drag_torque(self, drag_coefficient):
    #     "Calculate the magnitude of the force opposed to the direction of rotation"
    #     # Angular drag is a completely different calculation from translational drag

    #     air_density = self.environment.get_air_density(self.altitude)

    #     # Some of the radius multiplications come from converting angular velocity to tangent velocity
    #     # just totally ignore shear angular drag and use the equation CD * pi * h * density * Angular velocity ^ 2 * radius ^ 4 from https://physics.stackexchange.com/questions/304742/angular-drag-on-body
    #     # TODO: Check when shear stress is important (possibly for very thin rockets?)

    #     # This radius is wrong. Should be the radius of the rotating circle?
    #     # TODO: Fix the radius
    #     drag_around = drag_coefficient * np.pi * self.length * air_density * \
    #         (self.angular_velocity[0] ** 2) * self.radius ** 4
    #     drag_down = drag_coefficient * np.pi * self.length * air_density * \
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
    #     # TODO: Check if dist_grav_press is correct here
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
