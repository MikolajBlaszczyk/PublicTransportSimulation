from pandas import DataFrame
from simpy import Environment

from data.Bus import Bus
from data.Stop import Stop
from utils.Constant import DOOR_OPERATION_TIME, TIME_PER_BOARD, TIME_PER_DEPARTURE, BUS_CAPACITY


def bus_generator(env: Environment, routes: dict[(str, int), DataFrame],
                  starting_times_df: DataFrame, stops: dict[str, Stop], metrics):
    starting_times_df = starting_times_df.sort_values(by="arrival_time")

    for _, trip in starting_times_df.iterrows():
        arrival_seconds = (trip["arrival_time"].hour * 3600 +
                           trip["arrival_time"].minute * 60 +
                           trip["arrival_time"].second)
        wait_time = max(arrival_seconds - env.now, 0)
        yield env.timeout(wait_time)
        route = routes[(trip["route_id"], trip["direction_id"])]
        bus = Bus(name=trip["trip_id"], route_id=trip["route_id"],
                  stops=list(zip(route["stop_id"], route["next_stop_travel_time"])),
                  direction=trip["direction_id"], start_time=trip["arrival_time"], capacity=BUS_CAPACITY)

        print(f"{env.now:.1f}s: Bus spawned at {arrival_seconds}: {bus}")
        metrics['onboard'][bus.name] = []
        env.process(bus_process(env, bus, stops, metrics))

def bus_process(env, bus: Bus, stops: dict[str, Stop], metrics):
    onboard = metrics['onboard'][bus.name]
    for i, (stop_id, next_stop_travel_time) in enumerate(bus.stops):
        stop = stops[stop_id]
        with stop.request() as request:
            yield request
            print(f"{env.now:.1f}s: {bus.name} arrived at stop {stop_id}")
            to_departure = [passanger for passanger in list(onboard) if passanger.destination == stop_id]
            for departing_passanger in to_departure:
                onboard.remove(departing_passanger)
                departing_passanger.departure_timestamp = env.now
                metrics['records'].append(departing_passanger)
            number_of_departured_passangers = len(to_departure)

            number_of_boarded_passengers = 0
            if (i + 1) < len(bus.stops):
                to_board = [p for p in stop.passengers if p.destination in bus.stops[i + 1:][0]]
            else:
                to_board = []
            for b in to_board:
                if len(onboard) < bus.capacity:
                    stop.passengers.remove(b)
                    onboard.append(b)
                    b.board_timestamp = env.now
                    number_of_boarded_passengers += 1
                else:
                    break

            onboarding_and_departure_time = DOOR_OPERATION_TIME + TIME_PER_BOARD * number_of_boarded_passengers + TIME_PER_DEPARTURE * number_of_departured_passangers
            yield env.timeout(onboarding_and_departure_time)
        print(f"{env.now:.1f}s: {bus.name} departed from stop {stop_id} (Boarded: {number_of_boarded_passengers}, Departured: {number_of_departured_passangers}) Onboard: {len(onboard)}")
        if next_stop_travel_time is not None:
            yield env.timeout(next_stop_travel_time)
            # Could add traffic time delays here as well