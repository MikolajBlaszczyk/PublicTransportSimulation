from enum import Enum

class BusState(Enum):
    Boarding = 'Boarding'
    Waiting = 'Waiting'
    Traveling = 'Traveling'
    Finished = 'Finished'

class Bus:
    def __init__(self, stops: list[tuple[str, float]], name, route_id, direction, start_time, capacity):
        self.name = name
        self.route_id = route_id # bus line identifier
        self.stops = stops
        self.direction = direction
        self.capacity = capacity
        self.start_time = start_time
        self.stop_index = 0
        self.passengers_count = 0
        self.state = BusState.Waiting
        self.start_trip_seconds = 0
    def __str__(self):
        return f"Bus {self.name} on route {self.route_id} direction {self.direction} starting at {self.start_time.strftime('%H:%M')}"

    def get_state(self):
        return {
            "name": self.name,
            "route_id": self.route_id,
            "direction": self.direction,
            "state": self.state,
            "start_trip_seconds": self.start_trip_seconds,
            "current_stop_id": self.stops[self.stop_index][0] if self.stop_index < len(self.stops) else None,
            "next_stop_id": self.stops[self.stop_index + 1][0] if self.stop_index + 1 < len(self.stops) else None,
            "travel_time_seconds": self.stops[self.stop_index][1] if self.stop_index < len(self.stops) else None,
            "passengers_count": self.passengers_count,
        }