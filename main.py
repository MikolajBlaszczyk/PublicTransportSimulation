import pandas as pd
import simpy
import random
from collections import deque
import statistics

from data.Bus import Bus
from data.Stop import Stop
from simulation.BusProcessing import bus_process
from simulation.PassangerGenerator import passenger_generator
from simulation.StopsGenerator import generate_stops
from utils.Constant import BUS_CAPACITY, RANDOM_SEED, SIMULATION_TIME
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
    gtfs_data = gtfs_where_lines(data_path, lines)
    stops_graph = generate_directed_graph(gtfs_data)

    ## Czas trasy
    trips_times_df = gtfs_data["trips"].groupby(["route_id", "direction_id"])[["trip_id", "service_id", "trip_headsign"]].first()
    times_df = gtfs_data["stop_times"].merge(trips_times_df, on="trip_id")
    routes = {}
    for start_time in trips_times_df.itertuples():
        routes[start_time[0]] = times_df[times_df.trip_id == start_time.trip_id][["stop_id", "arrival_time"]]

    for key, values in routes.items():
        # Upewnij się, że arrival_time jest typu datetime
        values["arrival_time"] = pd.to_datetime(values["arrival_time"])
        # Różnica pomiędzy kolejnymi arrival_time

        values["next_stop_travel_time"] = values["arrival_time"].shift(-1) - values["arrival_time"]
        values["next_stop_travel_time"] = values["next_stop_travel_time"].dt.total_seconds()  # w sekundach

    # routes[(route_id, direction_id)] => DataFrame z kolumnami: stop_id, arrival_time, next_stop_travel_time
    ##

    ## Starty tras
    starting_times_df = (
        gtfs_data["trips"]
        .merge(
            gtfs_data["stop_times"].loc[gtfs_data["stop_times"].stop_sequence == 1],
            on="trip_id"
        )[
            ["trip_id", "route_id", "direction_id", "stop_id", "arrival_time"]
        ]
    )

    starting_times_grouped = {}

    for (route_id, direction_id), group in starting_times_df.groupby(["route_id", "direction_id"]):
        group = group.copy()
        group["arrival_time"] = (
            (group["arrival_time"] - group["arrival_time"].dt.normalize())
            .dt.total_seconds()
            .astype(int)
        )

        starting_times_grouped[(route_id, direction_id)] = (
            group[["arrival_time"]]
            .drop_duplicates()
            .sort_values(by="arrival_time")
        )

    # starting_times_grouped[(route_id, direction_id)] => DataFrame z kolumnami: arrival_time (w sekundach od północy)
    ##

    env = simpy.Environment()
    stops = generate_stops(env, stops_graph)
    metrics = {'generated': 0, 'records': [], 'incomplete': [], 'onboard': {}}

    busses = list()
    for key, values in routes.items():
        for start_time in starting_times_grouped[key]["arrival_time"]:
            busses.append(Bus(
                name=f"{key[0]}-{start_time}",
                route_id=key[0],
                direction=key[1],
                stops=list(zip(values["stop_id"], values["next_stop_travel_time"])),
                start_time=start_time,
                capacity=BUS_CAPACITY))

    env.process(passenger_generator(env, stops, stops_graph, metrics))

    for bus in busses:
        metrics['onboard'][bus.name] = []

    for bus in busses:
        env.process(bus_process(env, bus, stops, metrics))

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