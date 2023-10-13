
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


def plot_feature(data: pd.DataFrame, horizontal: Feature, *verticals: Feature):
    plt.xlabel(horizontal.get_label())
    y_labels = [vertical.name for vertical in verticals]
    y_label = ", ".join(y_labels)
    plt.ylabel(y_label + f"[{verticals[0].units.name}]")

    plt.title(f"{y_label} vs {horizontal.name}")

    for vertical in verticals:
        plt.plot(data[horizontal.get_label()], data[vertical.get_label()], label=vertical.name)

    if len(verticals) > 1:
        plt.legend()

# Time is always an attribute of the simulation.
feature_time = Feature("time", "time", Units.s)