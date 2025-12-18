from simpy import Environment

from data.Bus import Bus, BusState
from data.Stop import Stop
from utils.Constant import DOOR_OPERATION_TIME, TIME_PER_BOARD, TIME_PER_DEPARTURE, BUS_CAPACITY, DEBUG_PRINT
from utils.BusDataProcessing import BusGenerationData


def bus_generator(env: Environment, bus_generation_data: BusGenerationData, stops: dict[str, Stop], metrics):

    # Assuming that bus_generation_data.creation_df is already sorted by arrival_time
    for _, trip in bus_generation_data.creation_df.iterrows():
        arrival_seconds = (trip["arrival_time"].hour * 3600 +
                           trip["arrival_time"].minute * 60 +
                           trip["arrival_time"].second)
        wait_time = max(arrival_seconds - env.now, 0)
        yield env.timeout(wait_time)
        route = bus_generation_data.schedule_dict[(trip["route_id"], trip["direction_id"])]
        bus = Bus(name=trip["trip_id"], route_id=trip["route_id"],
                  stops=list(zip(route["stop_id"], route["travel_time"])),
                  direction=trip["direction_id"], start_time=trip["arrival_time"], capacity=BUS_CAPACITY)
        if DEBUG_PRINT:
            print(f"{env.now:.1f}s: Bus spawned at {arrival_seconds}: {bus}")
        metrics['onboard'][bus.name] = []
        bus_generation_data.buses.append(bus)
        env.process(bus_process(env, bus, stops, metrics))

def bus_process(env, bus: Bus, stops: dict[str, Stop], metrics):
    onboard = metrics['onboard'][bus.name]
    for i, (stop_id, travel_time) in enumerate(bus.stops):
        bus.stop_index = i
        stop = stops[stop_id]
        with stop.request() as request:
            bus.state = BusState.Waiting
            yield request
            bus.state = BusState.Boarding
            if DEBUG_PRINT:
                print(f"{env.now:.1f}s: {bus.name} arrived at stop {stop_id}")
            to_departure = [passenger for passenger in list(onboard) if passenger.destination == stop_id]
            for departing_passenger in to_departure:
                onboard.remove(departing_passenger)
                departing_passenger.departure_timestamp = env.now
                metrics['records'].append(departing_passenger)
            number_of_departed_passengers = len(to_departure)

            number_of_boarded_passengers = 0
            if (i + 1) < len(bus.stops):
                to_board = [p for p in stop.passengers if p.destination in bus.stops[i + 1:][0]]
            else:
                to_board = []
            for boarding_passenger in to_board:
                if len(onboard) < bus.capacity:
                    stop.passengers.remove(boarding_passenger)
                    onboard.append(boarding_passenger)
                    boarding_passenger.board_timestamp = env.now
                    number_of_boarded_passengers += 1
                else:
                    break

            bus.passengers_count = len(onboard)
            onboarding_and_departure_time = DOOR_OPERATION_TIME + TIME_PER_BOARD * number_of_boarded_passengers + TIME_PER_DEPARTURE * number_of_departed_passengers
            yield env.timeout(onboarding_and_departure_time)
        if DEBUG_PRINT:
            print(f"{env.now:.1f}s: {bus.name} departed from stop {stop_id} (Boarded: {number_of_boarded_passengers}, Departed: {number_of_departed_passengers}) Onboard: {len(onboard)}")
        if travel_time is not None:
            bus.state = BusState.Traveling
            yield env.timeout(travel_time)
            # Could add traffic time delays here as well
    bus.state = BusState.Finished