import numpy as np
import pandas as pd


class Logger:
    "Logs only the data"

    def __init__(self, rocket, to_record):
        self.rows = []
        # Use the actual rocket object to determine the data
        self.rocket = rocket
        self.to_record = to_record
        self.current_row = {}



    def add_items(self, data):
        self.current_row.update(data)

    def save_row(self):
        self.rows.append(self.current_row)
        self.current_row = {}


    def handle_frame(self):
        for key in self.to_record:
            self.add_items({key: self.rocket.__dict__[key]})

        self.save_row()

    def save_to_csv(self):
        df = pd.DataFrame(self.rows)
        df.set_index('time', inplace=True)

        df.to_csv("Data/Output/output.csv")


class Feedback_Logger(Logger):
    "Logs the progress of the rocket simulation"

    def __init__(self, rocket, to_record):
        print("Launching rocket")
        self.p_turned = False
        self.p_thrusted = False

        super().__init__(rocket, to_record)

    def handle_frame(self):
        super().handle_frame()

        if not self.p_turned and self.rocket.turned:
            print('Reached the turning point at %.3s seconds with a height of %.5s meters' % (
                self.rocket.environment.time, self.rocket.position[1]))
            self.p_turned = True

        if not self.p_thrusted and self.rocket.motor.finished_thrusting:
            print('Finished thrusting after %.3s seconds' %
                  self.rocket.environment.time)
            self.p_thrusted = True

        if self.rocket.position[1] <= 0:
            print(
                "Rocket landed with a speed of %.3s m/s after %.4s seconds of flight time" %
                (np.linalg.norm(self.rocket.velocity),
                 self.rocket.environment.time))


    def save_to_csv(self):
        super().save_to_csv()

        print("Saved the trial to csv")
