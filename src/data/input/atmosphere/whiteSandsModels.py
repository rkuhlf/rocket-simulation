# FITTED FUNCTIONS FOR WSMR WIND
# Store the data input methods generated in the FitWind.py file


import numpy as np

def piecewise_linear(x, a1, a2, a3, a4, m1, m2, m3, m4, m5, b1, b2, b3, b4, b5):
    mask1 = (x <= a1) * 1
    
    mask2 = (a1 < x) * (x <= a2)

    mask3 = (a2 < x) *  (x <= a3)

    mask4 = (a3 < x) *  (x <= a4)

    mask5 = (x > a4) * 1

    return mask1 * (x * m1 + b1) + mask2 * (x * m2 + b2) + mask3 * (x * m3 + b3) + mask4 * (x * m4 + b4) + mask5 * (x * m5 + b5)

def speed_at_altitude(altitude):
    return piecewise_linear(altitude, *[5.00000000e+02, 7.00000000e+03, 1.07000000e+04, 1.50000000e+04, 3.71317848e-03, 4.91875591e-04,1.35766566e-03,-1.44743481e-03,1.06007134e-03,3.08666400e+00,4.18071491e+00,-2.03629372e+00,2.86053477e+01,-9.20780533e+00])


if __name__ == "__main__":
    print(speed_at_altitude(8000))
