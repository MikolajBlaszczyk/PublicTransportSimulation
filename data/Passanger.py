class Passenger:
    _id = 0

    def __init__(self, origin, destination, destination_arrival_time):
        self.id = Passenger._id
        Passenger._id += 1
        self.origin = origin
        self.destination = destination # cos nie tak z nazwami 
        self.destination_arrival_time = destination_arrival_time # cos nie tak z nazwami
        self.board_timestamp = None
        self.departure_timestamp = None
