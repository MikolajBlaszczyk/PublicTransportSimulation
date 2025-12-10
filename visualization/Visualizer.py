import networkx as nx
import matplotlib.pyplot as plt

def visualize(gtfs_data):
    G = nx.DiGraph()

    for _, stop in gtfs_data["stops"].iterrows():
        label = f"{stop['stop_name']} {stop['stop_desc']}"
        G.add_node(
            stop["stop_id"],
            name=stop["stop_name"],
            lat=stop["stop_lat"],
            lon=stop["stop_lon"],
            label=label,
        )

    # 2. Posortuj stop_times
    stop_times = gtfs_data["stop_times"].sort_values(
        by=["trip_id", "stop_sequence"]
    )

    # 3. Dodaj krawędzie (przystanek -> kolejny przystanek w kursie)
    for _, trip in stop_times.groupby("trip_id"):
        stops = trip["stop_id"].tolist()

        for i in range(len(stops) - 1):
            G.add_edge(stops[i], stops[i + 1])

    pos = {
        stop["stop_id"]: (stop["stop_lon"], stop["stop_lat"])
        for _, stop in gtfs_data["stops"].iterrows()
    }

    labels = {node: data.get("label", node) for node, data in G.nodes(data=True)}

    plt.figure(figsize=(12, 12))
    nx.draw(G, pos, labels=labels, node_size=2, edge_color="black", alpha=0.2, with_labels=True)
    plt.show()