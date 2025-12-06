from collections import deque


class Stop:
    def __init__(self, name):
        self.name = name
        self.passanger_queue = deque()
