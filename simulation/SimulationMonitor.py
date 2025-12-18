from simpy import Environment

from utils.BusDataProcessing import BusGenerationData
from utils.Constant import MONITOR_SNAPSHOT_INTERVAL
from utils.StopDataProcessing import StopsGenerationData

def transport_monitor(env: Environment,
                      bus_generation_data: BusGenerationData,
                      stops_data: StopsGenerationData,
                      start_offset_seconds,
                      snapshots):
        yield env.timeout(start_offset_seconds - 20)
        while True:
            snap = {
                'time': env.now,
                'buses': [bus.get_state() for bus in bus_generation_data.buses],
                'stops': {
                    stop_id: {
                        'passengers_waiting': len(stop.passengers)
                    } for stop_id, stop in stops_data.resources_dict.items()
                }
            }
            snapshots.append(snap)
            yield env.timeout(MONITOR_SNAPSHOT_INTERVAL)