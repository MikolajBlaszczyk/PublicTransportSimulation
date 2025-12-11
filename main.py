import simpy
import random
from collections import deque
import statistics

from data.Stop import Stop
from simulation.BusProcessing import bus_process
from simulation.PassangerGenerator import passenger_generator
from utils.Constant import BUS_CAPACITY, RANDOM_SEED, SIMULATION_TIME


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
    gtfs_data = gtfs_where_lines(data_path, lines)
    stops_graph = generate_directed_graph(gtfs_data)

   

    env = simpy.Environment()
    stops = {n: Stop(env, n, 1) for n in ['A', 'B', 'C', 'D', 'E']}
    metrics = {'generated': 0, 'records': [], 'incomplete': [], 'onboard': {}}


    env.process(passenger_generator(env, stops['A'], metrics))


    route1 = ['A', 'B', 'C', 'E']
    route2 = ['A', 'B', 'D', 'E']


    metrics['onboard']['Bus-1'] = []
    metrics['onboard']['Bus-2'] = []


    env.process(bus_process(env, 'Bus-1', route1, stops, BUS_CAPACITY, metrics, start_delay=30.0))
    env.process(bus_process(env, 'Bus-2', route2, stops, BUS_CAPACITY, metrics, start_delay=90.0))

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