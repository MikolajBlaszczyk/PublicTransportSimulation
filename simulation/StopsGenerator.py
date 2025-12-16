from networkx import DiGraph
from simpy import Environment

from data.Stop import Stop
from utils.Constant import STOP_CAPACITY


def generate_stops(env: Environment, stops_graph: DiGraph) -> dict[str, Stop]:
    stops = {}

    for stop_id in stops_graph.nodes():
        stops[stop_id] = Stop(env, stop_id, capacity=STOP_CAPACITY)
    return stops