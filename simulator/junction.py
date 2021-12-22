from typing import List

from simulator.schedule import PeriodicSchedule, Schedule
from road import Road


class Junction:
    """
    Analogous to a vertex in the road graph

    Attributes
    ----------
    name: name of the junction
    in_rds: roads into the junction (since this is a directed graph)
    out_rds: roads out of the junction
    schedule: traffic light sequence at this junction
    """

    def __init__(self, name,
                 in_rds: List[Road] = None,
                 out_rds: List[Road] = None,
                 duration: List[int] = None):
        if duration is None:
            duration = []
        if in_rds is None:
            in_rds = []
        if out_rds is None:
            out_rds = []
        self.name = name
        self.out_rds = []
        self.in_rds = []
        assert (len(in_rds) == len(duration))
        self.schedule: Schedule = PeriodicSchedule(self, duration)

    def tick(self, t):
        in_rd = self.schedule.get_incoming_at(t)
        in_rd.deque().turn()

    def __str__(self):
        return f'Junction<{self.name}>'
