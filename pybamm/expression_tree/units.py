#
# Units class
#
import re
import pybamm
from collections import defaultdict

KNOWN_UNITS = [
    "m",
    "kg",
    "s",
    "A",
    "K",
    "mol",
    "cd",
    "h",
    "V",
    "J",
    "W",
    "S",
    "F",
    "C",
    "Ohm",
]


class Units:
    """A node containing information about units. This is usually an attribute of a node
    in the expression tree, and is automatically created by the expression tree

    Parameters
    ----------
    units : str
        units of the node
    """

    def __init__(self, units):
        # encode empty units
        if units is None or units == {}:
            self.units_str = "[-]"
            self.units_dict = defaultdict(int)
        elif isinstance(units, str):
            self.units_str = units
            self.units_dict = self.str_to_dict(units)
        else:
            units = defaultdict(int, units)
            self.units_str = self.dict_to_str(units)
            self.units_dict = units

        # Check all units are recognized
        for name in self.units_dict.keys():
            if name not in KNOWN_UNITS:
                raise pybamm.UnitsError(
                    "Unit '{}' not recognized".format(name)
                    + "\nKNOWN_UNITS: {}".format(KNOWN_UNITS)
                )

    def __str__(self):
        return self.units_str

    def __repr__(self):
        return "Units({!s})".format(self)

    def str_to_dict(self, units_str):
        "Convert string representation of units to a dictionary"
        # Extract from square brackets
        if units_str[0] != "[" or units_str[-1] != "]":
            raise pybamm.UnitsError(
                "Units should start with '[' and end with ']' (found '{}')".format(
                    units_str
                )
            )
        units_str = units_str[1:-1]
        # Find all the units and add to the dictionary
        units = units_str.split(".")
        units_dict = defaultdict(int)
        for unit in units:
            # Look for negative
            if "-" in unit:
                # Split by the location of the negative
                name = unit[: unit.index("-")]
                amount = unit[unit.index("-") :]
                # amount automatically includes the negative by the way it is extracted
            else:
                # Split by character and number
                match = re.match(r"([a-z]+)([0-9]+)", unit, re.I)
                if match:
                    name, amount = match.groups()
                else:
                    # If no number was found, it must be a '1', e.g. 'm' in 'm.s-1'
                    name = unit
                    amount = 1
            # Add the unit to the dictionary
            units_dict[name] = int(amount)

        # Update units dictionary for special parameters
        units_dict = self.reformat_dict(units_dict)

        return units_dict

    def dict_to_str(self, units_dict):
        "Convert a dictionary of units to a string representation"
        # O(n2) but the dictionary is small so it doesn't matter
        # First loop through the positives
        units_str = ""

        # Update units dictionary for special parameters
        units_dict = self.reformat_dict(units_dict)

        for name, amount in sorted(units_dict.items()):
            if amount == 0:
                raise pybamm.UnitsError("Zero units should not be in dictionary")
            elif amount == 1:
                # Don't record the amount if there's only 1, e.g. 'm.s-1' instead of
                # 'm1.s-1'
                units_str += name + "."
            elif amount > 1:
                units_str += name + str(amount) + "."
        # Then loop through the negatives
        for name, amount in sorted(units_dict.items()):
            if amount < 0:
                # The '-' is already in the amount
                units_str += name + str(amount) + "."

        # Remove the final '.'
        units_str = units_str[:-1]

        return "[" + units_str + "]"

    def reformat_dict(self, units_dict):
        "Reformat units dictionary"
        if "J" in units_dict:
            num_J = units_dict.pop("J")
            units_dict["V"] += num_J
            units_dict["C"] += num_J
        if "C" in units_dict:
            num_C = units_dict.pop("C")
            units_dict["A"] += num_C
            units_dict["s"] += num_C
        if "W" in units_dict:
            num_W = units_dict.pop("W")
            units_dict["V"] += num_W
            units_dict["A"] += num_W
        if "S" in units_dict:
            num_S = units_dict.pop("S")
            units_dict["A"] += num_S
            units_dict["V"] -= num_S
        if "Ohm" in units_dict:
            num_Ohm = units_dict.pop("Ohm")
            units_dict["V"] += num_Ohm
            units_dict["A"] -= num_Ohm
        return units_dict

    def __add__(self, other):
        if self.units_dict == other.units_dict:
            return Units(self.units_dict)
        else:
            raise pybamm.UnitsError(
                "Cannot add different units {!s} and {!s}".format(self, other)
            )

    def __sub__(self, other):
        if self.units_dict == other.units_dict:
            return Units(self.units_dict)
        else:
            raise pybamm.UnitsError(
                "Cannot subtract different units {!s} and {!s}".format(self, other)
            )

    def __mul__(self, other):
        # Add common elements and keep distinct elements
        # remove from units dict if equal to zero
        mul_units = {
            k: self.units_dict.get(k, 0) + other.units_dict.get(k, 0)
            for k in set(self.units_dict) | set(other.units_dict)
            if self.units_dict.get(k, 0) + other.units_dict.get(k, 0) != 0
        }
        return Units(mul_units)

    def __truediv__(self, other):
        # Subtract common elements and keep distinct elements
        # remove from units dict if equal to zero
        div_units = {
            k: self.units_dict.get(k, 0) - other.units_dict.get(k, 0)
            for k in set(self.units_dict) | set(other.units_dict)
            if self.units_dict.get(k, 0) - other.units_dict.get(k, 0) != 0
        }
        return Units(div_units)

    def __pow__(self, power):
        # Multiply units by the power
        # This is different from the other operations in that "power" has to be an
        # integer
        pow_units = {k: power * v for k, v in self.units_dict.items()}
        return Units(pow_units)

    def __eq__(self, other):
        "Two units objects are defined to be equal if their unit_dicts are equal"
        return self.units_dict == other.units_dict
