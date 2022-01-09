from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulator.junction import Junction
from simulator.util import get_bin_idx


class Schedule:
    """
    Represent a traffic light schedule at a junction, serves as an interface

    Attributes
    ----------
    junction: each traffic light must be associated with a junction
    schedule: a function that takes in time and output which road the deque should occur
              uses random sampling by default
    """

    def __init__(self, junction: Junction, schedule=None):
        self.junction = junction
        self.schedule = schedule

    def get_incoming_at(self, t):
        if self.schedule:
            return self.schedule(t)
        else:
            return random.choice(self.junction.in_rds)


class PeriodicSchedule(Schedule):
    """
    Represent a traffic light schedule that releases traffic in a round-robin fashion periodically

    Attributes
    ----------
    junction, schedule: same as parent class
    """

    def __init__(self, junction: Junction, duration):
        super().__init__(junction)
        self.schedule = lambda t: self.junction.in_rds[get_bin_idx(duration, t)]
