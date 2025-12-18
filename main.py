import simpy
import random
import statistics

from simulation.BusProcessing import bus_generator
from simulation.PassangerGenerator import passenger_generator
from utils.Constant import RANDOM_SEED, SIMULATION_TIME
from utils.BusDataProcessing import prepare_bus_generation_data
from utils.GtfsParser import gtfs_where_lines
from utils.StopDataProcessing import prepare_stops_generation_data

random.seed(RANDOM_SEED)

# TODO:
# Bardziej inteligentni agenci (autobusy i pasazerowie) - P1
# Reserch toola do wizualizacji symulacji - P2

# Info:
# Paradygmaty DES i AGS - chyba ...

def run():
    data_path = "./data/GTFS_KRK_A.zip"
    lines = ["189", "511"]
    env = simpy.Environment()
    gtfs_data = gtfs_where_lines(data_path, lines)
    stops_data = prepare_stops_generation_data(gtfs_data, env)

    bus_generation_data = prepare_bus_generation_data(gtfs_data)

    metrics = {'generated': 0, 'records': [], 'incomplete': [], 'onboard': {}}

    start_time_offset = bus_generation_data.creation_df["arrival_time"].min()
    env.process(passenger_generator(env, stops_data, start_time_offset, metrics))
    env.process(bus_generator(env, bus_generation_data, stops_data.resources_dict, metrics))

    env.run(until=SIMULATION_TIME)

    completed = [r for r in metrics['records'] if r.board_timestamp is not None and r.departure_timestamp is not None]
    waits = [p.board_timestamp - p.destination_arrival_time for p in completed]
    in_vehicle = [p.departure_timestamp - p.board_timestamp for p in completed]


    incomplete_onboard = sum(len(lst) for lst in metrics['onboard'].values())
    waiting_at_stops = sum(len(s.passengers) for s in stops_data.resources_dict.values())

    print(f"Generated passengers: {metrics['generated']}")
    print(f"Completed trips: {len(completed)}")
    if waits:
        print(f"Mean wait: {statistics.mean(waits):.1f}s, median: {statistics.median(waits):.1f}s")
    if in_vehicle:
        print(f"Mean in-vehicle: {statistics.mean(in_vehicle):.1f}s")
    print(f"Incomplete trips (onboard at end): {incomplete_onboard}")
    print(f"Passengers still waiting at stops: {waiting_at_stops}")


if __name__ == "__main__":
    run()