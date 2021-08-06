import numpy as np
from Helpers.general import vector_from_angle, angle_between, combine, magnitude, angled_cylinder_cross_section
from Helpers.fluidSimulation import cutout_method, barrowman_equation, extended_barrowman_equation
from Data.Input.models import get_coefficient_of_drag


# TODO: Factor in changing center of gravity
# TODO: get approximate position of motor so that I can recalculate center of gravity every frame
# It should be do-able with only the initial center of gravity (and mass), and the position of the motor and the mass that is lost



from Helpers.general import interpolate

# also includes any libraries that are imported in this file
from preset_object import PresetObject

# Have a separate fin class?


class Rocket(PresetObject):
    def post_load_initialization(self):
        self.update_previous()

        # maybe should make an addmotor method
        self.mass += self.motor.mass
        self.mass += self.parachute.mass


        # Indicates whether the rocket has begun to descend
        self.turned = False
        self.landed = False

    def __init__(
            self, config={},
            environment=None, motor=None, parachute=None, logger=None):
        # X, Y, Z values, where Z is upwards
        self.position = np.array([0, 0, 0], dtype="float64")
        self.velocity = np.array([0, 0, 0], dtype="float64")
        self.acceleration = np.array([0, 0, 0], dtype="float64")

        # TODO: Implement a sort of framework class
        # It holds all of the information about the rocket's shape. Then I can put some of the barrowman stuff in there
        # It also throws you a message if the engine wouldn't fit

        # Using rotation around, rotation down. Later I will add roll, but I think the effects are too complicated atm
        # Using global rotation, not relative rotation based on the rocket
        # TODO: Make sure that I am converting the torque into radians. I think I might have to divided by dist_pressure & gravity
        # When rotation is zero (measured in radians), the rocket is headed straight up
        # It's against safety procedures to launch at an angle more than 30 degrees from vertical
        # Unless there is wind, rotation around (index zero) should not change at all; That part is working correctly
        self.rotation = np.array(
            [np.pi / 2, -0.05],
            dtype="float64")
        self.angular_velocity = np.array([0, 0], dtype="float64")
        self.angular_acceleration = np.array([0, 0], dtype="float64")

        # This is just the mass of the frame, the motor and propellant will be added in a second
        self.mass = 1.86  # kg

        self.radius = 0.05  # meters
        self.height = 2  # meters

        # This is actually a relatively large difference, but hopefully increasing it will slow down rotation
        self.center_of_gravity = 1.0  # meters from the nose tip
        self.center_of_pressure = 1.8  # meters from the nose tip

        self.dist_gravity_pressure = self.center_of_pressure - self.center_of_gravity


        # Calculate using http://www.rasaero.com/dl_software_ii.htm
        # TODO: figure out a way to simulate this so that it works in 3D
        # Probably the theoretical best thing to do is to calculate the drag coefficient of the object rotated so that the relative velocity is only in one dimension. Calculating separate drag coefficients for two components of velocity doesn't make sense, so it is necessary to rotate the shape so that it is at the same angle against a one component velocity, find the consequent drag force, then combine that to the unrotated force
        # This is basically a cached value
        self.drag_coefficient = 0
        self.drag_coefficient_perpendicular = 1.08
        self.moment_of_inertia = 0


        self.vertical_area = np.pi * self.radius ** 2  # 0.008  # m^2
        self.sideways_area = self.radius * 2 * self.height  # 0.4 m^2

        # This is overriden in the simulation initialization
        self.apply_angular_forces = True

        self.motor = motor
        self.environment = environment
        self.parachute = parachute
        self.logger = logger

        # Everything before this is saved as a preset
        super().overwrite_defaults(config)


        self.post_load_initialization()



    def reset(self):
        super().reset()
        self.post_load_initialization()

    def update_previous(self):
        """Update the variables that hold last frame's rocket features"""
        self.p_position = np.copy(self.position)  # p stands for previous
        self.p_velocity = np.copy(self.velocity)
        self.p_acceleration = np.copy(self.acceleration)

        self.p_rotation = np.copy(self.rotation)
        self.p_angular_velocity = np.copy(self.angular_velocity)
        self.p_angular_acceleration = np.copy(self.angular_acceleration)

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

    def calculate_moment_of_inertia(self):
        # FIXME: Actually this sucks and is complicated because moment of inertia isn't a scalar quantity for a complex 3d shape
        # use calculated value from Fusion 360/Other CAD, currently using random one for a cylinder
        self.moment_of_inertia = 1 / 12 * self.mass * self.height ** 2

    def calculate_drag_coefficient(self):
        self.drag_coefficient = get_coefficient_of_drag(self.get_mach())

    def calculate_center_of_pressure(self):
        cutout = cutout_method()
        barrowman = barrowman_equation()

        self.center_of_pressure = extended_barrowman_equation(
            self.get_angle_of_attack(), barrowman, cutout)



    def calculate_center_of_gravity(self):
        pass

    def calculate_cp_cg_dist(self):
        self.dist_press_grav = self.center_of_pressure - self.center_of_gravity

    def get_angle_of_attack(self):
        return angle_between(
            self.velocity, vector_from_angle(self.rotation))

    def get_drag_torque(self, drag_coefficient):
        "Calculate the magnitude of the force opposed to the direction of rotation"
        # Angular drag is a completely different calculation from translational drag

        air_density = self.environment.get_air_density(self.get_altitude())

        # Some of the radius multiplications come from converting angular velocity to tangent velocity
        # just totally ignore shear angular drag and use the equation CD * pi * h * density * Angular velocity ^ 2 * radius ^ 4 from https://physics.stackexchange.com/questions/304742/angular-drag-on-body
        # TODO: Check when shear stress is important (possibly for very thin rockets?)
        # The coefficient of drag is the same as for linear drag atm, but I actually think it's okay

        # This radius is wrong. Should be the radius of the rotating circle?
        # TODO: Fix the radius
        drag_around = drag_coefficient * np.pi * self.height * air_density * \
            (self.angular_velocity[0] ** 2) * self.radius ** 4
        drag_down = drag_coefficient * np.pi * self.height * air_density * \
            (self.angular_velocity[1] ** 2) * self.radius ** 4

        # should be opposite the direction of motion
        if np.sign(self.angular_velocity[0]) == np.sign(drag_around):
            drag_around *= -1
        if np.sign(self.angular_velocity[1]) == np.sign(drag_down):
            drag_down *= -1


        return drag_around, drag_down

    def calculate_torque(self, force):
        "Calculate the torque caused by an arbitrary force"
        # The drag force fully applies to the translational motion of the rocket, but it also fully applies to the rotational momentum of the object
        # calculate the torque in two perpendicular directions
        torque = np.array([0., 0.])
        if not np.all(force == 0):

            # Perpendicular is slightly more complicated in 3D. We need the component of the force that is perpendicular to the current rotation of the rocket. To me, it seems like the easiest thing is to break the force down into each of it's components and calculate that individually
            z_component = force[2]
            # The z component cannot cause rotation around, only affecting theta down
            z_component_perpendicular = z_component * \
                np.sin(self.theta_down())
            # When rocket is completely horizontal (90 degrees), it should apply 100%, when vertical, 0%. This is sine.

            # a torque in the vertical direction (positive z component), should cause an increase in theta down
            torque[1] += self.dist_gravity_pressure * z_component_perpendicular



            x_component = force[0]
            # The around rotation determines what fraction of the force goes to the yaw and what fraction to the torque. When the rocket hasn't spun at all, all of the x_component goes to the pitch
            # I might just need the magnitude of this
            pitch_multiplier = np.cos(self.theta_around())
            # If the rocket was travelling horizontally, there wouldn't be any force. 90 -> 0
            angle_of_incidence_multiplier = np.cos(self.theta_down())

            torque[1] -= x_component * pitch_multiplier * \
                angle_of_incidence_multiplier * self.dist_gravity_pressure


            # Only apply the leftover x to the yaw
            yaw_multiplier = np.sin(self.theta_around())
            # When the rocket is horizontal, however, the yaw will still be fully applied. I don't think I need any other multiplier

            torque[0] += x_component * yaw_multiplier * self.dist_gravity_pressure

            y_component = force[1]
            pitch_multiplier = np.sin(self.theta_around())
            angle_of_incidence_multiplier = np.cos(self.theta_down())

            torque[1] -= y_component * pitch_multiplier * \
                angle_of_incidence_multiplier * self.dist_gravity_pressure


            yaw_multiplier = np.cos(self.theta_around())
            # x and y can't cause yaw in the same direction (I think, so we'll just have them be opposite)
            torque[0] -= y_component * yaw_multiplier * self.dist_gravity_pressure

            # self.logger.add_items(
            #   {"Yaw torque after y translational drag": torque[0].copy()})



        # ANGULAR DRAG CALCULATION
        # This should definitely be a different function. What if I want to have separate calls to find translational torque
        # This rotation drag is always in the opposite direction of angular velocity. Be aware that that isn't always the same as the direction of torque due to translation
        # It is in the 10 ^ -4 range. That seems like it is too low to cause the rotation to converge
        # The impulse that this supplies should never be bigger than the impulse that the rocket is rotating with. TODO: Figure out how to calculate the momentum of rotation an object has (mv -> moment of inertia * rotational velocity)
        # TODO: Check if dist_rav_press is correct ere
        current_rotational_momentum = self.moment_of_inertia * \
            self.angular_velocity * self.dist_gravity_pressure

        # Thoug it isn't exactly great design, I think that around drag should use drag_coefficient_perpendicular and down_drag should also use the perpendicular. This is an approximation
        around_drag, down_drag = self.get_drag_torque(
            self.drag_coefficient_perpendicular)

        # FIXME: this is not how it works anymore. Rather than applying a force opposite the angle, we need to make sure three components are pointing the opposite way. Somehow I need to figure out if it is overdoing it in any direction TODO: Add back in

        def more_than_cancels(initial, change):
            return abs(change) > abs(initial) and np.sign(change) != np.sign(
                initial)

        if more_than_cancels(
                current_rotational_momentum[0],
                around_drag * self.environment.time_increment):
            # This actually has an effect a significant portion of the time
            around_drag = current_rotational_momentum[0] / \
                self.environment.time_increment

        if more_than_cancels(
                current_rotational_momentum[1],
                down_drag * self.environment.time_increment):
            # This actually has an effect a significant portion of the time
            down_drag = current_rotational_momentum[1] / \
                self.environment.time_increment


        # This is making almost zero difference
        # No multiplication by dist_grav_press. If center of mass and center of pressure were identical, the object would still experience angular drag
        torque[0] += around_drag
        torque[1] += down_drag

        return torque


    def get_drag_force(self, area, drag_coefficient):
        "Calculate the magnitude of the translational drag force"

        air_density = self.environment.get_air_density(self.get_altitude())

        self.logger.add_items(
            {"area": area})

        coeff = air_density * area * drag_coefficient / 2

        relative_velocity = self.velocity - \
            self.environment.get_air_speed(self.get_altitude())

        base_magnitude = magnitude(relative_velocity)
        self.logger.add_items(
            {"mag": base_magnitude})
        # No div by 0 error
        if np.isclose(base_magnitude, 0):
            return np.array([0., 0., 0.])

        air_resistance = np.array([0., 0., 0.])

        squared_magnitude = base_magnitude ** 2


        relative_velocity *= squared_magnitude / base_magnitude

        self.logger.add_items(
            {"squared_magnitude": magnitude(relative_velocity)})

        self.logger.add_items(
            {"coeff": coeff})
        # self.logger.add_items(
        #     {"squared_magnitude": magnitude(relative_velocity)})
        air_resistance = coeff * -relative_velocity



        self.logger.add_items(
            {"Direction of translational drag": air_resistance.copy()})

        return air_resistance

    # Maybe have an add force function which takes a distance from the nose tip
    def calculate_forces(self):
        # Forces don't carry over from frame to frame, so we need to set them back to zero
        # The full force is applied in the fector direction that it has
        total_force = np.array([0., 0., 0.])
        # Only the perpendicular component is applied to the rotation
        rotating_force = np.array([0., 0., 0.])

        # There is a constant gravitational force downwards
        # ADD RAVITY back in
        total_force[2] -= self.environment.get_gravitational_attraction(
            self.mass, self.get_altitude())


        # This will have to change. Need to get the new drag coefficient at run time

        angle_of_attack = self.get_angle_of_attack()

        # This is correct, but it is going to give some pretty fucked up results without a variable (with angle) center of pressure. Extended barrowman should solve that issue
        # This is actually only sort of correct. Basically, the drag force calculation is expecting a reference area. That just means that however we determined our coefficients of drag, that is how we should determine the area. Since it is probably easiest just to use fattest cross section each time, it is unnecessary. Again, it depends on how the calculation for CD is done.
        area = angled_cylinder_cross_section(
            angle_of_attack, self.radius, self.height)

        drag_force = self.get_drag_force(
            area, self.drag_coefficient)

        total_force += drag_force

        # TODO: Research the 'Normal Force Coefficient'
        # I'm still slightly concerned about this - I'm pretty sure not all of the energy of the air is applied to rotating the rocket. It is inelastic-ish, but I think that ish plays a big enough role that you can't just assume it's 100%. I'm not even sure if the word inelastic applies
        # changing this to a minus sign here, will have to change some other stuff when the sim starts
        # It should be something like rotating_force -= drag_force * 0.5, but I can't figure out what
        rotating_force += drag_force  # Force eventually added to the velocity



        thrust = self.motor.get_thrust(self.environment.time)

        # thrust is in direction of the rotation. The larger the angle is, the more to the right the rocket is
        directed_thrust = thrust * vector_from_angle(self.rotation)
        # self.logger.add_items({'thrust': directed_thrust})
        # directed_thrust = np.reshape(thrust * unit_direction, (3,))


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



    def apply_acceleration(self):
        combined_acceleration = combine(
            self.p_acceleration, self.acceleration)
        self.velocity += combined_acceleration * self.environment.time_increment

        combined_velocity = combine(self.p_velocity, self.velocity)
        self.position += combined_velocity * self.environment.time_increment


    def simulate_step(self):
        if self.logger is not None:
            self.logger.add_items({'time': self.environment.time})

        # Recalculate cached values
        self.calculate_drag_coefficient()
        self.calculate_moment_of_inertia()
        # self.calculate_center_of_pressure()
        # self.calculate_center_of_gravity()
        # self.calculate_cp_cg_dist()

        total_force, rotating_force = self.calculate_forces()
        # Adds in the rotational drag
        torque = self.calculate_torque(rotating_force)


        self.angular_acceleration = torque / self.moment_of_inertia
        self.apply_angular_acceleration()

        self.acceleration = total_force / self.mass
        self.apply_acceleration()


        if self.position[2] <= 0:
            self.landed = True

        if self.position[2] < self.p_position[2]:
            self.turned = True

            # TODO: Figure out how parachute deployment mechanisms tend to work. Is it always as soon as it turns? How long does it take? Calculate the forces on the parachute chord
            # self.parachute.deploy(self)

        self.update_previous()
