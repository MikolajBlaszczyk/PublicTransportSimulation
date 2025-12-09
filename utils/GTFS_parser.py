import zipfile
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from utils.Schema import GTFS_SCHEMA
from typing import Dict

def load_gtfs(zip_path: str) -> Dict[str, pd.DataFrame]:
    """
    Load a GTFS ZIP file and apply appropriate datatypes.

    Args:
    zip_path: path to GTFS .zip file
    dtypes: optional dict to override or extend GTFS_SCHEMA

    Returns:
    dict[str, DataFrame]
    """
    schema = GTFS_SCHEMA.copy()

    data = {}

    with zipfile.ZipFile(zip_path, "r") as z:
        for filename in z.namelist():
            if not filename.endswith(".txt"):
                continue

            name = filename[:-4]  # remove .txt
            base_dtypes = schema.get(name, {})

            # Load all fields as strings first to preserve formatting
            df = pd.read_csv(z.open(filename), dtype=str, keep_default_na=False)

            # Then safely convert selected fields to target types
            for col, dtype in base_dtypes.items():
                if col not in df.columns:
                    continue
                try:
                    if dtype == float:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    elif dtype in (int, "Int64"):
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                    elif dtype == "datetime":
                        df[col] = pd.to_datetime(df[col], format="%H:%M:%S", errors="coerce")
                    else:
                        df[col] = df[col].astype(str)
                except Exception:
                    pass

            data[name] = df

    return data

gtfs_data = load_gtfs("../data/GTFS_KRK_A.zip")


for stop in gtfs_data["stops"].itertuples():
    print(f"{stop.stop_name} {stop.stop_desc} {stop.stop_lat} {stop.stop_lon}")

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

plt.figure(figsize=(12,12))
nx.draw(G, pos, labels=labels, node_size=2, edge_color="black", alpha=0.2, with_labels=True)
plt.show()