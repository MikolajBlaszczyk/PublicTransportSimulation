import networkx as nx


def generate_directed_graph(gtfs_data):
    di_graph = nx.DiGraph()

    for _, stop in gtfs_data["stops"].iterrows():
        label = f"{stop['stop_name']} {stop['stop_desc']}"
        di_graph.add_node(
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
            di_graph.add_edge(stops[i], stops[i + 1])

    return di_graph