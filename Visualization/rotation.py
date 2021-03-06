import matplotlib.pyplot as plt
import numpy as np

# TODO: graph rotation over time
# Should osciallate
# Use to double check the derived equation is correct


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
