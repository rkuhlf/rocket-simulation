from random import gauss

def random_WSMR_temperature():
    """ Returns reasonable distribution of ox tank starting temperatures
    https://workflowy.com/s/ox-tank-temperatures/uyeOIq6AbgfvoOoY"""
    return gauss(288.7, 5.6)
