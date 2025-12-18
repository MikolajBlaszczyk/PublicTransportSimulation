
class Bus:
    def __init__(self, stops: list[tuple[str, float]], name, route_id, direction, start_time, capacity):
        self.name = name
        self.route_id = route_id # bus line identifier
        self.stops = stops
        self.direction = direction
        self.capacity = capacity
        self.start_time = start_time
    def __str__(self):
        return f"Bus {self.name} on route {self.route_id} direction {self.direction} starting at {self.start_time.strftime('%H:%M')}"