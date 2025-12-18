__all__ = ["BusGenerationData", "prepare_bus_generation_data"]

import pandas as pd
from typing import Dict

class BusGenerationData: 
    def __init__(self, creation_df: pd.DataFrame, schedule_dict: dict[tuple, pd.DataFrame]):
        self.creation_df = creation_df
        self.schedule_dict = schedule_dict
        self.buses = []

def prepare_merged_df(gtfs: Dict[str, pd.DataFrame]):
    routes_df =  gtfs["routes"][["route_id"]]
    trips_df = gtfs["trips"][["trip_id", "route_id", "trip_headsign", "direction_id"]]
    stops_times_df = gtfs["stop_times"][["trip_id", "arrival_time", "stop_id", "stop_sequence"]]
    stop_df = gtfs["stops"][["stop_id", "stop_name", "stop_lat", "stop_lon"]]

    return routes_df.merge(trips_df, on="route_id").merge(stops_times_df, on="trip_id").merge(stop_df, on="stop_id")

def prepare_creation_df(merged_df: pd.DataFrame) -> pd.DataFrame: 
    creation_df = merged_df[(merged_df["stop_sequence"] == 1)]
    creation_df = creation_df[["trip_id", "stop_id", "arrival_time",  "route_id", "direction_id"]]

    creation_df["arrival_time"] = creation_df["arrival_time"].dt.time

    creation_df.sort_values(by="arrival_time", inplace=True)

    return creation_df

def prepare_schedule_df(merged_df: pd.DataFrame):
    seeked_tripId_df = merged_df.drop_duplicates(subset=["route_id", "direction_id"], keep="first")["trip_id"]
    scheme_df = merged_df[(merged_df["trip_id"].isin(seeked_tripId_df))].sort_values(["trip_id", "stop_sequence"])

    scheme_df["next_stop_id"] = scheme_df.groupby("trip_id")["stop_id"].shift(-1)
    scheme_df["next_arrival_time"] = scheme_df.groupby("trip_id")["arrival_time"].shift(-1)

    scheme_df["arrival_time"] = pd.to_datetime(scheme_df["arrival_time"], format='%H:%M:%S', errors='coerce')
    scheme_df["next_arrival_time"] = pd.to_datetime(scheme_df["next_arrival_time"], format='%H:%M:%S', errors='coerce')
    scheme_df["travel_time"] = (scheme_df["next_arrival_time"] - scheme_df["arrival_time"]).dt.total_seconds()

    scheme_df = scheme_df[["route_id",  "direction_id", "stop_id", "next_stop_id", "stop_sequence", "travel_time"]]

    scheme_dict = {
        key: group.drop(columns=["route_id", "direction_id"])
        for key, group in scheme_df.groupby(["route_id", "direction_id"])
    }
    
    return scheme_dict

def prepare_bus_generation_data(gtfs: Dict[str, pd.DataFrame]):
    merged_df = prepare_merged_df(gtfs)
    creation_df = prepare_creation_df(merged_df)
    scheme_dict = prepare_schedule_df(merged_df)

    return BusGenerationData(creation_df, scheme_dict)