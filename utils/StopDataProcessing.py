import networkx as nx
from networkx import DiGraph
from pandas import DataFrame
from simpy import Environment

from data.Stop import Stop
from utils.Constant import STOP_CAPACITY


class StopsGenerationData:
    def __init__(self, graph: DiGraph, objects: dict[str, Stop]):
        self.graph = graph
        self.objects_dict = objects

def generate_directed_graph(gtfs_data):
    di_graph = nx.DiGraph()

    for _, stop in gtfs_data["stops"].iterrows():
        label = f"{stop['stop_name']} {stop['stop_desc']}"
        di_graph.add_node(
            stop["stop_id"],
            name=stop["stop_name"],
            lat=stop["stop_lat"],
            lon=stop["stop_lon"],
            label=label,
        )

    stop_times = gtfs_data["stop_times"].sort_values(
        by=["trip_id", "stop_sequence"]
    )

    for _, trip in stop_times.groupby("trip_id"):
        stops = trip["stop_id"].tolist()

        for i in range(len(stops) - 1):
            di_graph.add_edge(stops[i], stops[i + 1])

    return di_graph

def generate_stops(env: Environment, stops_graph: DiGraph) -> dict[str, Stop]:
    stops_dict = {}

    for stop_id in stops_graph.nodes():
        stops_dict[stop_id] = Stop(env, stop_id, capacity=STOP_CAPACITY)
    return stops_dict

def prepare_stops_generation_data(gtfs: dict[str, DataFrame], env: Environment) -> StopsGenerationData:
    graph = generate_directed_graph(gtfs)
    stops_dict = generate_stops(env, graph)

    return StopsGenerationData(graph, stops_dict)