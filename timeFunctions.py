from timeit import timeit
import importlib
from Helpers.timing import Timer



# One Trial: 24.7
def test_overall_speed():
    with Timer():
        # this one isn't going to work for multiple trials
        # I think if you just reset the variables.py it might work
        importlib.import_module('rocket')




if __name__ == "__main__":
    test_overall_speed()
