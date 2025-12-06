from utils.Constant import DOOR_OPERATION_TIME, TIME_PER_BOARD, TIME_PER_DEPARTURE, TRAVEL_TIME


def bus_process(env, bus_name, route, stops_map, capacity, metrics, start_delay=0.0):
  
    if start_delay > 0:
        yield env.timeout(start_delay)

 

    onboard = metrics['onboard'][bus_name]

    while True:
        for i, stop_name in enumerate(route):
  
            to_departure = [passanger for passanger in list(onboard) if passanger.destination == stop_name]
            for departing_passanger in to_departure:
                onboard.remove(departing_passanger)
                departing_passanger.departure_timestamp = env.now
                metrics['records'].append(departing_passanger)
            number_of_departured_passangers = len(to_departure)


            stop = stops_map[stop_name]
            number_on_board = 0

            while stop.passanger_queue and len(onboard) < capacity:
                candidate = stop.passanger_queue[0]
                if candidate.destination in route[i+1:]:
                    p = stop.passanger_queue.popleft()
                    p.board_timestamp = env.now
                    onboard.append(p)
                    number_on_board += 1
                else:
                    break


            onboarding_and_departure_time = DOOR_OPERATION_TIME + TIME_PER_BOARD * number_on_board + TIME_PER_DEPARTURE * number_of_departured_passangers
            yield env.timeout(onboarding_and_departure_time)
          
            if i < len(route) - 1:
                yield env.timeout(TRAVEL_TIME)