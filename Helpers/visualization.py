# STANDARD FUNCTIONS FOR VISUALIZATION

import matplotlib
import matplotlib.pyplot as plt


def make_matplotlib_big():
    font = {'family' : 'DejaVu Sans',
        # 'weight' : 'bold',
        'size'   : 22}

    matplotlib.rc('font', **font)

    matplotlib.rc('legend', fontsize=15)


def make_matplotlib_medium():
    font = {'family' : 'DejaVu Sans',
        # 'weight' : 'bold',
        'size'   : 15}

    matplotlib.rc('font', **font)

    matplotlib.rc('legend', fontsize=12) 