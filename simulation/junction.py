from typing import List

from simulation.schedule import Schedule, PeriodicSchedule
from simulation.road import Road


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
        self.name = name
        self.in_rds = in_rds or []
        self.out_rds = out_rds or []

        if duration:
            assert (len(in_rds) == len(duration))
            self.schedule: Schedule = PeriodicSchedule(self, duration)
        else:
            self.schedule = Schedule(self)

    def tick(self, t):
        in_rd = self.schedule.get_incoming_at(t)
        car = in_rd.deque()
        if car:
            car.advance()

    def __str__(self):
        return f'Junction<{self.name}>'
