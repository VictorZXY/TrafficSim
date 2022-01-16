from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulation.junction import Junction
from simulation.util import get_bin_idx


class Schedule:
    """
    Represent a traffic light schedule at a junction, serves as an interface

    Attributes
    ----------
    schedule: a function that takes in time and output which road the dequeue should occur
              uses random sampling by default
    """

    def __init__(self, schedule=None):
        self.schedule = schedule or (lambda _: 0)

    def get_incoming_at(self, t):
        return self.schedule(t)


class PeriodicSchedule(Schedule):
    """
    Represent a traffic light schedule that releases traffic in a round-robin fashion periodically

    Attributes
    ----------
    schedule: same as parent class
    """

    def __init__(self, duration):
        super().__init__()
        self.schedule = lambda t: get_bin_idx(duration, t)
