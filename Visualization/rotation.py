import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# TODO: graph rotation of the actual data over time
# Should osciallate
# Use to double check the derived equation is correct

# TODO: derive equations for these graphs using calculus


# SIMPLIFIED REPRESENTATION OF ROCKET ANGLE:
# Takeaways - regardless of the multiplier on the acceleration, the angle will never converge
# That means that no matter how dense the air is, or drag heavy the rocket is, it will continue oscillating at the exact same rate
# Therefore, angular drag *does* have to be working correctly, and it is definitely not negligable
def graphSimple():
    # Graph an angle
    # Every step, we subtract the sin of the angle with a multiplier
    # At what multiplier does the amplitude start to expand, and when does it contract
    time_record = []
    t = 0

    angle_record = []
    angle = 0.1

    angle_velocity_record = []
    angle_velocity = 0

    force_record = []
    force = 0

    # This multiplier represents the effects of the speed of the rocket, the density, and the drag coefficient
    multiplier = 0.01  # starts expanding around pi / 2 (I think)

    iters = 100

    for _ in range(iters):
        time_record.append(t)
        t += 1

        angle_record.append(angle)


        force = multiplier * np.sin(angle)
        force_record.append(force)

        angle_velocity -= force
        angle_velocity_record.append(angle_velocity)

        angle += angle_velocity

    plt.plot(time_record, angle_record)
    # plt.plot(time_record, angle_velocity_record)


    plt.show()


def graphCompleteWithArbitraryCoefficients():
    time_record = []
    t = 0

    angle_record = []
    angle = 0.1

    angle_velocity_record = []
    angle_velocity = 0

    # Represents the torque that drag force provides due to the differing COP and COG
    force_record = []
    force = 0

    # Represents the torque that air resistance provides on the rotating object
    drag_record = []
    drag = 0

    # This multiplier represents the effects of the translational speed of the rocket, the density, and the drag coefficient
    # If it is too high (like 5), the rocket does start to spin out of control
    multiplier = 0.2  # starts expanding around pi / 2 (I think)


    # The higher this multiplier, the quicker it compresses, regardless of the multiplier for torque caused by translation
    # That means that if the rocket starts spinning, it is because there isn't enough angular drag
    # I don't think it should have anything to do with the perpendicular component of drag
    drag_multiplier = 1

    iters = 100

    for _ in range(iters):
        time_record.append(t)
        t += 1

        angle_record.append(angle)


        force = multiplier * np.sin(angle)
        force_record.append(force)

        drag = drag_multiplier * angle_velocity ** 2
        drag *= np.sign(angle_velocity)
        drag_record.append(drag)

        angle_velocity -= force + drag
        angle_velocity_record.append(angle_velocity)

        angle += angle_velocity

    plt.plot(time_record, angle_record)
    plt.plot(time_record, drag_record)
    plt.plot(time_record, force_record)


    plt.show()


# Based on this it seems that the rocket is experiencing too much torque due to air resistance
def graphRocketOutput():
    df = pd.read_csv("Data/Output/output.csv")
    # Convert it out of a 1,1 array
    df['rotation'] = df['rotation'].apply(lambda x: float(x[1:-1]))

    df.plot(x='time', y='rotation', kind='line')

    plt.show()






























if __name__ == "__main__":
    # graphCompleteWithArbitraryCoefficients()
    graphRocketOutput()
