# Map of expected GTFS datatypes per file (string, float, int)
# All fields default to string unless specified.
GTFS_SCHEMA = {
    "stops": {
        "stop_lat": float,
        "stop_lon": float,
        "location_type": "Int64",
        "wheelchair_boarding": "Int64",
    },
    "routes": {
        "route_type": "Int64",
    },
    "trips": {
        "direction_id": "Int64",
        "wheelchair_accessible": "Int64",
        "bikes_allowed": "Int64",
    },
    "stop_times": {
        "arrival_time": "datetime",
        "departure_time": "datetime",
        "stop_sequence": "Int64",
        "pickup_type": "Int64",
        "drop_off_type": "Int64",
        "shape_dist_traveled": float,
        "timepoint": "Int64",
    },
    "calendar": {}, # There are other fields, but we won't use them now
    "calendar_dates": {
        "exception_type": "Int64",
    },
    "shapes": {
        "shape_pt_lat": float,
        "shape_pt_lon": float,
        "shape_pt_sequence": "Int64",
        "shape_dist_traveled": float,
    },
    "agency": {},
    "blocks": {},
}