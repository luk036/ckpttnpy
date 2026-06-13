"""K-way constraint manager for FM partitioning.

FMKWayConstrMgr extends FMConstrMgr with per-partition illegal tracking
for k-way partitions. A move is AllSatisfied only when all parts meet
the lower bound after the move.
"""

from typing import Any, Dict, List, Union

# Check if the move of v can satisfied, makebetter, or NotSatisfied
from .FMConstrMgr import FMConstrMgr, LegalCheck

Part = Union[Dict[Any, int], List[int]]


class FMKWayConstrMgr(FMConstrMgr):
    """The `FMKWayConstrMgr` class is a subclass of `FMConstrMgr` (Fiduccia-Mattheyses Constraint Manager) that initializes with a list of illegal parts."""

    def __init__(self, hyprgraph, bal_tol, module_weight, num_parts: int):
        r"""
        The function initializes an object with certain parameters and sets all elements of the "illegal"
        list to True.

        :param hyprgraph: The `hyprgraph` parameter is a type that is not specified in the code snippet. It is likely a
            custom type or a reference to another class or module
        :param bal_tol: The `bal_tol` parameter is used to specify the balance tolerance for the module. It
            represents the maximum allowable difference in weight between the heaviest and lightest parts in the
            module
        :param module_weight: The `module_weight` parameter represents the weight of a single module
        :param num_parts: The `num_parts` parameter is an integer that represents the number of parts in the
            system
        :type num_parts: int
        """
        FMConstrMgr.__init__(self, hyprgraph, bal_tol, module_weight, num_parts)
        self.illegal = [True] * num_parts

    def init(self, part: Part):
        """
        The `init` function initializes the `illegal` attribute by checking if each element in `self.diff`
        is less than `self.lowerbound`.

        :param part: The `part` parameter is of type `Part` and it represents some part of an object or system
        :type part: Part
        """
        FMConstrMgr.init(self, part)
        self.illegal = [d < self.lowerbound for d in self.diff]

    def select_togo(self):
        """
        The function `select_togo` returns the index of the minimum value in the `diff` list.
        :return: The index of the minimum value in the list `self.diff`.
        """
        return min(range(self.num_parts), key=lambda k: self.diff[k])

    def check_legal(self, move_info_v):
        """

        The function `check_legal` checks if a move is legal and returns the status of the move.



        :param move_info_v: The `move_info_v` parameter is a tuple containing three elements. The first

            element is not used in this function. The second element, `from_part`, represents the part from

            which the move is being made. The third element, `to_part`, represents the part to which the move is being

        :return: the value of the variable "status". If "status" is not equal to "LegalCheck.AllSatisfied",

            then the function will return the value of "status". Otherwise, it will return "LegalCheck.AllSatisfied".



        .. svgbob::



            "K-Way Constraint Checking"

          +----------------+----------------+----------------+

          |  Part 0        |  Part 1        |  Part 2        |

          |  weight: 25    |  weight: 35    |  weight: 20    |

          |  [v1, v2]      |  [v3, v4, v5]  |  [v6, v7]      |

          |  illegal: True |  illegal: True |  illegal: False |

          +----------------+----------------+----------------+



          Check if moving v5 from Part 1 to Part 2 makes all parts legal

        """

        status = FMConstrMgr.check_legal(self, move_info_v)

        if status != LegalCheck.AllSatisfied:
            return status

        _, from_part, to_part = move_info_v

        self.illegal[from_part] = self.illegal[to_part] = False

        if any(self.illegal):
            return LegalCheck.GetBetter  # get better, but still illegal

        return LegalCheck.AllSatisfied  # all satisfied
