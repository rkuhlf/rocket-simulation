
from lib.chemistry import ideal_gas_pressure, van_der_waals_pressure


if __name__ == "__main__":

    inputs = [
        # m^3,  K, moles
        [0.05, 100, 200]
    ]

    a = 0.3832
    b = 0.04415 * 0.001

    for args in inputs:
        print(f"Ideal {ideal_gas_pressure(*args):.0f}; Non-Ideal: {van_der_waals_pressure(*args, a, b):.0f}")