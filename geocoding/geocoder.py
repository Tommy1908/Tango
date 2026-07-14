import json
import os
from geopy.geocoders import Photon
from schemas import count_dict, operation_dict
from typing import Any, cast
from shapely.geometry import Point


class Geocoder:
    def __init__(self):
        self.geolocator = Photon(timeout=5) # type: ignore

    def geocode_address(self, address:str, city="Ciudad Autónoma de Buenos Aires", country="Argentina") -> tuple[float,float] | None:
    
        query = f"{address}, {city}, {country}"

        try:
            location = cast(Any, self.geolocator.geocode(query))
            if location:
                return (round(location.latitude, 7), round(location.longitude, 7))
        except Exception as e:
            print(f"API error (Photon): {e}")

        return None
    
    def geocode_count(self, count: list[count_dict], saved_path = "") -> list[operation_dict]:
        result = []
        saved = {}
        if saved_path != "" and os.path.exists(saved_path):
            with open(saved_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                saved = {item["name"]: item["coordinates"] for item in data}

        for item in count:
            if item["name"] in saved:
                coordinates = saved[item["name"]]
            else:
                coordinates = self.geocode_address(item["address"])

            result.append({
                "name": item["name"],
                "address": item["address"],
                "count": item["count"],
                "coordinates": coordinates
            })
        return result
    
    def classify_by_zone(self, coordinate, zones) -> list[str]:
        coordinate_zones = []
        coordinate_point = Point(coordinate)

        for zone, polygon in zones.items():
            if polygon.contains(coordinate_point):
                coordinate_zones.append(zone)
        return coordinate_zones
    
    def classfy_count_by_zone(self, operation_dict:list[operation_dict], zones) -> list[operation_dict]:
        for item in operation_dict:
            if item["coordinates"]:
                item["zone"] = self.classify_by_zone(item["coordinates"], zones)
            else:
                item["zone"] = []
        return operation_dict
    
    def save_located_coords(self, operation_dict:list[operation_dict], path) -> None:
        # Not saving zones, it might change more often, and is not that expensive to compute
        save_data = []
        for item in operation_dict:
            save_item = item.copy()
            save_item.pop('count', None) 
            save_data.append(save_item)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=4)

if __name__ == "__main__": # pragma: no cover
    address = "ARENALES 1210"
    geocoder = Geocoder()
    print(f"{address}:{geocoder.geocode_address(address)}")

    address = "MONTEVIDEO 937"
    geocoder = Geocoder()
    print(f"{address}:{geocoder.geocode_address(address)}")