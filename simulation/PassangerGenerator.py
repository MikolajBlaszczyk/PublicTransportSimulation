import random
from data.Passanger import Passenger
from utils.Constant import PASSENGER_MEAN_INTERARRIVAL


def passenger_generator(env, stop, metrics):
    while True:
        yield env.timeout(random.expovariate(1.0 / PASSENGER_MEAN_INTERARRIVAL))
        destination_choice = random.choice(['C', 'D', 'E'])
        passanger = Passenger('A', destination_choice, env.now)
        stop.passanger_queue.append(passanger)
        metrics['generated'] += 1
