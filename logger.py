import numpy as np
import pandas as pd


class Logger:
    "Logs only the data"

    def __init__(self, rocket, to_record, target="output.csv"):
        self.rows = []
        # Use the actual rocket object to determine the data
        self.rocket = rocket
        self.splitting_arrays = False
        self.to_record = to_record
        self.current_row = {}
        self.target = target



    def add_items(self, data):
        if self.splitting_arrays:
            k = list(data.keys())[0]
            v = list(data.values())[0]


            if isinstance(v, np.ndarray):
                if len(v) != 0:
                    data = {}
                    index = 1
                    for item in v:
                        data[k + str(index)] = item

                        index += 1

        self.current_row.update(data)

    def save_row(self):
        self.rows.append(self.current_row)
        self.current_row = {}

    def handle_frame(self):
        for key in self.to_record:
            self.add_items({key: self.rocket.__dict__[key].copy()})

        self.save_row()

    def save_to_csv(self):
        df = pd.DataFrame(self.rows)
        print(df)
        df.set_index('time', inplace=True)

        df.to_csv("Data/Output/" + self.target)

    def reset(self):
        self.__init__(self.rocket, self.to_record)


class Feedback_Logger(Logger):
    "Logs the progress of the rocket simulation along with some print statements"

    def __init__(self, rocket, to_record, target="output.csv"):
        print("Launching rocket")
        self.p_turned = False
        self.p_thrusted = False
        self.should_print_top_speed = True

        super().__init__(rocket, to_record, target)

    def handle_frame(self):
        super().handle_frame()

        if not self.p_turned and self.rocket.turned:
            print('Reached the turning point at %.3s seconds with a height of %.5s meters' % (
                self.rocket.environment.time, self.rocket.position[2]))
            self.p_turned = True
            self.should_print_top_speed

        # FIXME: Doesn't work because p_velocity = velocity in the rocket. Probably should check if y acceleration is in opposite direction to y velocit
        if self.should_print_top_speed:
            if np.sign(
                    self.rocket.velocity[2]) != np.sign(
                    self.rocket.acceleration[2]):
                print("Top speed was", np.linalg.norm(
                    self.rocket.velocity), " at Mach", self.rocket.get_mach())

                self.should_print_top_speed = False


        if not self.p_thrusted and self.rocket.motor.finished_thrusting:
            print('Finished thrusting after %.3s seconds' %
                  self.rocket.environment.time)
            self.p_thrusted = True

        # If the position off of the base altitude is less than or equal to zero, we hit the ground
        if self.rocket.position[2] < 0:
            print(
                "Rocket landed with a speed of %.3s m/s after %.4s seconds of flight time" %
                (np.linalg.norm(self.rocket.velocity),
                 self.rocket.environment.time))


    def save_to_csv(self):
        super().save_to_csv()

        print("Saved the trial to csv")
