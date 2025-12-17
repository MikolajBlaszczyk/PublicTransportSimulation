import random

from networkx.classes import DiGraph
from simpy import Environment

from data.Passenger import Passenger
from data.Stop import Stop
from utils.Constant import PASSENGER_MEAN_INTERARRIVAL


def passenger_generator(env: Environment, stops: dict[str, Stop], stops_graph: DiGraph, start_offset, metrics):
    # Przygotuj listę przystanków z następnikami
    valid_starts = [stop_id for stop_id in stops.keys()
                    if list(stops_graph.successors(stop_id))]

    start_offset_seconds = (start_offset.hour * 3600 +
                            start_offset.minute * 60 +
                            start_offset.second)

    yield env.timeout(start_offset_seconds - 20)
    while True:
        # yield env.timeout(random.expovariate(1.0 / PASSENGER_MEAN_INTERARRIVAL))
        yield env.timeout(10) # test value

        start_id = random.choice(valid_starts)
        successors = list(stops_graph.successors(start_id))
        end_id = random.choice(successors)

        passenger = Passenger(start_id, end_id, env.now)
        stops[start_id].passengers.append(passenger)
        metrics['generated'] += 1
        print(f"{env.now:.1f}s: Passenger generated at stop {start_id} heading to {end_id}")
