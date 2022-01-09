from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulator.car import Car


class Road:
    """
    Class representing roads, acting as a queue to record waiting cars

    Attributes
    ----------
    name: name of the road
    length: length of the road
    queue: queue of cars waiting at the road
    origin: starting junction of the road
    exit: ending junction of the road
    """
    def __init__(self, name, length, origin, exit):
        self.name = name
        self.length = length
        self.queue = []
        self.origin = origin
        self.exit = exit

    def deque(self) -> Car:
        return self.queue.pop() if self.queue else None

    def enqueue(self, car: Car):
        self.queue.append(car)

    def reset(self):
        self.queue = []

    def __str__(self):
        return f'Road<{self.name}>'
