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


feature_time = Feature("time", "time", Units.s)