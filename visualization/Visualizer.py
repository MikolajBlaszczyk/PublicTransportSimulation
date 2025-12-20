import networkx as nx
import matplotlib.pyplot as plt
from networkx import DiGraph

from data.Bus import BusState
from matplotlib.animation import FuncAnimation


def visualize(gtfs_data, graph: DiGraph, snapshots,
              interval=200,
              node_base_size=300,
              node_size_factor=50):
    pos = {
        stop["stop_id"]: (stop["stop_lon"], stop["stop_lat"])
        for _, stop in gtfs_data["stops"].iterrows()
    }

    fig, ax = plt.subplots(figsize=(12, 12))

    def interpolate(a, b, t):
        t = max(0.0, min(1.0, t))
        return (
            a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
        )

    def draw_buses(snapshot):
        for _, bus_data in enumerate(snapshot["buses"]):
            if bus_data['state'] in [BusState.Waiting, BusState.Boarding]:
                t = 0.0
            elif bus_data['state'] is BusState.Traveling:
                t = (snapshot['time'] - bus_data['start_trip_seconds']) / bus_data['travel_time_seconds']
            else:
                t = 0.75

            current_stop_id = bus_data['current_stop_id']
            next_stop_id = bus_data['next_stop_id']
            if next_stop_id is None:
                next_stop_id = current_stop_id
            if current_stop_id is None:
                continue
            x, y = interpolate(pos[current_stop_id], pos[next_stop_id], t)
            ax.scatter(x, y, s=node_base_size + bus_data['passengers_count'] * node_size_factor, zorder=5)
            ax.text(x, y, f"{bus_data['name']}: {bus_data['state'].value}", fontsize=8, zorder=6)

    def update(frame):
        ax.clear()
        snap = snapshots[frame]

        labels = {
            stop_id: f"{stop_id}: {passengers_waiting}"
            for stop_id, passengers_waiting in snap["stops"].items()
        }

        nx.draw(
            graph,
            pos,
            ax=ax,
            arrows=True,
            #labels=labels,
        )

        draw_buses(snap)
        ax.set_title(f"Time = {snap['time']}, {snap['time'] // 3600}:{(snap['time'] % 3600) // 60:02}:{snap['time'] % 60:02}")

    ani = FuncAnimation(
        fig,
        update,
        frames=len(snapshots),
        interval=interval,
        repeat=False
    )

    plt.show()
