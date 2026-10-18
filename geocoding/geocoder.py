from geopy.geocoders import Photon, Nominatim
from schemas import count_dict, operation_dict
from typing import Any, cast
from shapely.geometry import Point
import time

class Geocoder:
    def __init__(self):
        self.geolocator_Nominatim = Nominatim(timeout=5, user_agent="geocoding_for_arg") # type: ignore
        self.geolocator_Photon = Photon(timeout=5,  user_agent="geocoding_for_arg") # type: ignore


    def geocode_address(self, address:str, city="Ciudad Autónoma de Buenos Aires", country="Argentina") -> tuple[float,float] | None:
        query = f"{address}, {city}, {country}"
        print(f"Searching for: {address}")
        try:
            location = cast(Any, self.geolocator_Photon.geocode(query))
            if location:
                print(location)
                return (round(location.latitude, 7), round(location.longitude, 7))
        except Exception as e:
            print(f"API error (Photon): {e}")
        return None
    
    def geocode_count(self, count: list[count_dict], saved={}) -> list[operation_dict]:
        result = []
        has_null_coordiantes_names = []
        for destination in count:
            if destination["name"] in saved:
                coordinates = saved[destination["name"]]
            else:
                time.sleep(1) # Avoid api rate limit
                coordinates = self.geocode_address(destination["address"])
                if coordinates is None:
                    has_null_coordiantes_names.append(destination["name"])
            result.append({
                "name": destination["name"],
                "address": destination["address"],
                "count": destination["count"],
                "coordinates": coordinates
            })

        if has_null_coordiantes_names:
            raise ValueError(f"Algunas direcciones dieron NULL y deben arreglarse manualmente: {has_null_coordiantes_names}")

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
    
if __name__ == "__main__": # pragma: no cover
    geocoder = Geocoder()
    
    address = "ARENALES 1210"
    print(f"{address}:{geocoder.geocode_address(address)}")

    address = "MONTEVIDEO 937"
    print(f"{address}:{geocoder.geocode_address(address)}")