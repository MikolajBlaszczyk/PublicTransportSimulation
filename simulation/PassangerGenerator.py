import random

from networkx.classes import DiGraph
from simpy import Environment

from data.Passenger import Passenger
from data.Stop import Stop
from utils.Constant import PASSENGER_MEAN_INTERARRIVAL


def passenger_generator(env: Environment, stops: dict[str, Stop], stops_graph: DiGraph, metrics):
    # Przygotuj listę przystanków z następnikami
    valid_starts = [stop_id for stop_id in stops.keys()
                    if list(stops_graph.successors(stop_id))]

    while True:
        # yield env.timeout(random.expovariate(1.0 / PASSENGER_MEAN_INTERARRIVAL))
        yield env.timeout(10) # test value

        start_id = random.choice(valid_starts)
        successors = list(stops_graph.successors(start_id))
        end_id = random.choice(successors)

        passenger = Passenger(start_id, end_id, env.now)
        stops[start_id].passengers.append(passenger)
        metrics['generated'] += 1