import simpy
import random
import statistics

from simulation.BusProcessing import bus_generator
from simulation.PassangerGenerator import passenger_generator
from simulation.StopsGenerator import generate_stops
from utils.Constant import RANDOM_SEED, SIMULATION_TIME
from utils.DataPreProcessor import prepare_bus_generation_data
from utils.GraphGenerator import generate_directed_graph
from utils.GtfsParser import gtfs_where_lines

random.seed(RANDOM_SEED)

# TODO:
# Decyzja dotyczaca obszaru symulowanych linii autobusowych (3 linie na poczatek?) - P0
# Implementacja lini w networkX - P0
# Odpalenie symulacji z kilkoma roznymi metadanymi /utils/Constant.py - P0
# Bardziej inteligentni agenci (autobusy i pasazerowie) - P1
# Reserch toola do wizualizacji symulacji - P2

# Info:
# Paradygmaty DES i AGS - chyba ...

def run():
    data_path = "./data/GTFS_KRK_A.zip"
    lines = ["189", "511"]
    env = simpy.Environment()
    gtfs_data = gtfs_where_lines(data_path, lines)
    stops_graph = generate_directed_graph(gtfs_data)
    stops = generate_stops(env, stops_graph)

    bus_generation_data = prepare_bus_generation_data(gtfs_data)

    metrics = {'generated': 0, 'records': [], 'incomplete': [], 'onboard': {}}

    start_time_offset = bus_generation_data.creation_df["arrival_time"].min()
    env.process(passenger_generator(env, stops, stops_graph, start_time_offset, metrics))
    env.process(bus_generator(env, bus_generation_data, stops, metrics))

    env.run(until=SIMULATION_TIME)

    completed = [r for r in metrics['records'] if r.board_timestamp is not None and r.departure_timestamp is not None]
    waits = [p.board_timestamp - p.destination_arrival_time for p in completed]
    in_vehicle = [p.departure_timestamp - p.board_timestamp for p in completed]


    incomplete_onboard = sum(len(lst) for lst in metrics['onboard'].values())
    waiting_at_stops = sum(len(s.passengers) for s in stops.values())

    print(f"Generated passengers: {metrics['generated']}")
    print(f"Completed trips: {len(completed)}")
    if waits:
        print(f"Mean wait: {statistics.mean(waits):.1f}s, median: {statistics.median(waits):.1f}s") # cos nie dziala
    if in_vehicle:
        print(f"Mean in-vehicle: {statistics.mean(in_vehicle):.1f}s") # cos nie dziala 
    print(f"Incomplete trips (onboard at end): {incomplete_onboard}")
    print(f"Passengers still waiting at stops: {waiting_at_stops}")


if __name__ == "__main__":
    run()