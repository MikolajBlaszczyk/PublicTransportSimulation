import zipfile
import pandas as pd
from utils.Schema import GTFS_SCHEMA
from typing import Dict

def load_gtfs(zip_path: str) -> Dict[str, pd.DataFrame]:
    """
    Load a GTFS ZIP file and apply appropriate datatypes.

    Args:
    zip_path: path to GTFS .zip file

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

def stops_for_lon_and_lat(gtfs, min_point, max_point):
    """
    Return stops whose stop_lat and stop_lon lie inside the axis-aligned bounding box.
    `min` and `max` are tuples: (lat, lon).
    """
    stops = gtfs["stops"].copy()

    # Normalize bounds in case tuples were given in reverse
    min_lat = min_point[0]
    max_lat = max_point[0]
    min_lon = min_point[1]
    max_lon = max_point[1]

    mask = (
        (stops["stop_lon"] >= min_lon) & (stops["stop_lon"] <= max_lon) &
        (stops["stop_lat"] >= min_lat) & (stops["stop_lat"] <= max_lat)
    )

    return stops[mask]

def routes_for_lines_names(gtfs, line_names):
    """
    Return routes whose route_desc contains any of the substrings in route_short_names.
    """
    routes = gtfs["routes"].copy()

    mask = pd.Series([False] * len(routes))

    for name in line_names:
        mask |= routes["route_short_name"].str.contains(name, case=False, na=False)

    return routes[mask]


def gtfs_based_on_stops(gtfs):
    stop_ids = gtfs["stops"]["stop_id"].unique()
    # Pobierz wszystkie tripy odwiedzające podane przystanki
    stop_times = gtfs["stop_times"][gtfs["stop_times"]["stop_id"].isin(stop_ids)]
    trip_ids = stop_times["trip_id"].unique()

    # Pobierz route_id dla tych tripów
    filtered_trips = gtfs["trips"][gtfs["trips"]["trip_id"].isin(trip_ids)]
    route_ids = filtered_trips["route_id"].unique()

    # Zwróć tabele trips i routes
    filtered_routes = gtfs["routes"][gtfs["routes"]["route_id"].isin(route_ids)]

    gtfs_copy = gtfs.copy()
    gtfs_copy["stop_times"] = stop_times
    gtfs_copy["trips"] = filtered_trips
    gtfs_copy["routes"] = filtered_routes

    return gtfs_copy

def gtfs_based_on_routes(gtfs):
    route_ids = gtfs["routes"]["route_id"].unique()
    # Pobierz wszystkie tripy dla podanych route_id
    filtered_trips = gtfs["trips"][gtfs["trips"]["route_id"].isin(route_ids)]
    trip_ids = filtered_trips["trip_id"].unique()

    # Pobierz stop_times dla tych tripów
    filtered_stop_times = gtfs["stop_times"][gtfs["stop_times"]["trip_id"].isin(trip_ids)]
    stop_ids = filtered_stop_times["stop_id"].unique()

    # Pobierz przystanki
    filtered_stops = gtfs["stops"][gtfs["stops"]["stop_id"].isin(stop_ids)]

    gtfs_copy = gtfs.copy()
    gtfs_copy["stop_times"] = filtered_stop_times
    gtfs_copy["trips"] = filtered_trips
    gtfs_copy["stops"] = filtered_stops

    return gtfs_copy

def gtfs_where_lines(path, line_names):
    gtfs = load_gtfs(path)
    gtfs["routes"] = routes_for_lines_names(gtfs, line_names)
    gtfs = gtfs_based_on_routes(gtfs)
    return gtfs

def gtfs_where_area(path, min_point, max_point):
    gtfs = load_gtfs(path)
    gtfs["stops"] = stops_for_lon_and_lat(gtfs, min_point, max_point)
    gtfs = gtfs_based_on_stops(gtfs)
    return gtfs