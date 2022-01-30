from logging import Logger


# TODO: figure out how to make a class abstract in python
class FlightLogger(Logger):
    """
        Logs the progress of the rocket simulation along with some print statements.
    """


    def __init__(self, rocket, **kwargs):
        # You need to make sure the parent's override doesn't override the self values we have already established, so we set our defaults after this
        super().__init__(rocket)

        self.to_record = ['position', 'velocity', 'acceleration', 'rotation', 'angular_velocity',
        'angular_acceleration']


        self.debug_every = 20 # seconds

        self.overwrite_defaults(**kwargs)

        self.printed_rail_stats = False
        self.printed_thrusted = False
        self.turned = False

    # Make it so that you can access it via either the logging_object or rocket property
    @property
    def rocket(self):
        return self.logging_object

    # Function to translate CSVs into dataframes

    # Function to read CSVs into dataframes


    # Function to translate to another Flight Logger


    #region Header Names
    POSITION = "Displacement (m)"
    def get_position(self):
        raise NotImplementedError()

    POSITION_X = "X Position (m)"
    def get_position_x(self):
        raise NotImplementedError()
    
    POSITION_Y = "Y Position (m)"
    def get_position_y(self):
        raise NotImplementedError()

    POSITION_Z = "Z Position (m)"
    def get_position_z(self):
        raise NotImplementedError()


    VELOCITY = "Velocity Magnitude (m/s)"
    def get_velocity(self):
        raise NotImplementedError()

    VELOCITY_X = "X Velocity (m/s)"
    def get_velocity_x(self):
        raise NotImplementedError()

    VELOCITY_Y = "Y Velocity (m/s)"
    def get_velocity_y(self):
        raise NotImplementedError()
    
    VELOCITY_Z = "Z Velocity (m/s)"
    def get_velocity_z(self):
        raise NotImplementedError()


    ACCELERATION = "Acceleration Magnitude (m/s2)"
    def get_acceleration(self):
        raise NotImplementedError()

    ACCELERATION_X = "X Acceleration (m/s2)"
    def get_acceleration_x(self):
        raise NotImplementedError()

    ACCELERATION_Y = "Y Acceleration (m/s2)"
    def get_acceleration_y(self):
        raise NotImplementedError()

    ACCELERATION_Z = "Z Acceleration (m/s2)"
    def get_acceleration_z(self):
        raise NotImplementedError()



    ROTATION_AROUND = "Around (deg)"
    def get_rotation_around(self):
        raise NotImplementedError()

    ROTATION_DOWN = "Down (deg)"
    def get_rotation_down(self):
        raise NotImplementedError()


    ANGULAR_VELOCITY_AROUND = "Velocity Around (deg/s)"
    def get_angular_velocity_around(self):
        raise NotImplementedError()

    ANGULAR_VELOCITY_DOWN = "Velocity Down (deg/s)"
    def get_angular_velocity_down(self):
        raise NotImplementedError()


    ANGULAR_ACCELERATION_AROUND = "Acceleration Around (deg/s2)"
    def get_angular_acceleration_around(self):
        raise NotImplementedError()

    ANGULAR_ACCELERATION_DOWN = "Acceleration Down (deg/s2)"
    def get_angular_acceleration_down(self):
        raise NotImplementedError()

    #endregion

