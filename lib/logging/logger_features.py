
import matplotlib.pyplot as plt
import pandas as pd

from lib.units import Units
from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Feature:
    """
    Display names should be all lower case.
    Paths should follow the necessary object properties to reach the attribute.
    units should be in abbreviations, using negative exponents for fractions.
    """
    name: str
    path: str
    units: Units

    def get_label(self) -> str:
        return f"{self.name} [{self.units.value}]"


def plot_feature(data: pd.DataFrame, horizontal: Feature, vertical: Feature):
    plt.title(f"{vertical.name} vs {horizontal.name}")
    plt.xlabel(horizontal.get_label())
    plt.ylabel(vertical.get_label())
    plt.plot(data[horizontal.get_label()], data[vertical.get_label()])


# Time is always an attribute of the simulation.
feature_time = Feature("time", "time", Units.s)