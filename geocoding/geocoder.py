from geopy.geocoders import Photon, Nominatim
from schemas import count_dict, operation_dict
from typing import Any, cast
from shapely.geometry import Point
import time
import requests

class Geocoder:
    def __init__(self):
        self.geolocator_Nominatim = Nominatim(timeout=5, user_agent="geocoding_for_arg") # type: ignore
        self.geolocator_Photon = Photon(timeout=5,  user_agent="geocoding_for_arg") # type: ignore
        self.usig_address = "https://servicios.usig.buenosaires.gob.ar/normalizar/"

    def geocode_address(self, address: str) -> tuple[tuple[float, float],str] | tuple[None,None]:
        # Base on priority
        geocoders = [
            (self.geocode_usig, 'USIG'),
            (self.geocode_Photon, 'Photon'),
            (self.geocode_Nominatim, 'Nominatim')
        ]
        
        for geocode_func, source_name in geocoders:
            try:
                coords = geocode_func(address)
            except Exception as e:
                print(f"API error ({source_name}): {e}")
                continue
            if coords:
                return coords, source_name
                
        return None, None

    def geocode_usig(self, address: str) -> tuple[float, float] | None: # pragma: no cover
        print(f"Usig searching for: {address}")
        try:
            response = requests.get(
                self.usig_address,
                params={"direccion": f"{address}, CABA", "geocodificar": "true"},
                timeout=10,
            )
            response.raise_for_status()
            first_match = response.json()["direccionesNormalizadas"][0]
            lon, lat = first_match["coordenadas"]["x"], first_match["coordenadas"]["y"]

            return (round(float(lat), 7), round(float(lon), 7))
        except Exception as e:
            print(f"API error (USIG): {e}")
            return None

    def geocode_Photon(self, address:str, city="Ciudad Autónoma de Buenos Aires", country="Argentina") -> tuple[float,float] | None: # pragma: no cover
        query = f"{address}, {city}, {country}"
        print(f"Photon searching for: {address}")
        try:
            location = cast(Any, self.geolocator_Photon.geocode(query))
            if location:
                print(location)
                return (round(location.latitude, 7), round(location.longitude, 7))
        except Exception as e:
            print(f"API error (Photon): {e}")
        return None

    def geocode_Nominatim(self, address:str, city="Ciudad Autónoma de Buenos Aires", country="Argentina") -> tuple[float,float] | None: # pragma: no cover
        query = f"{address}, {city}, {country}"
        print(f"Nominatim searching for: {address}")
        try:
            location = cast(Any, self.geolocator_Nominatim.geocode(query))
            if location:
                print(location)
                return (round(location.latitude, 7), round(location.longitude, 7))
        except Exception as e:
            print(f"API error (Nominatim): {e}")
        return None

    
    def geocode_count(self, count: list[count_dict], saved={}) -> tuple[list[operation_dict],bool]:
        result = []
        has_null_coordiantes_names = []
        for destination in count:
            if destination["name"] in saved:
                coordinates = saved[destination["name"]]
                source = "SAVED"
                print(f"Restored {destination["name"]}")
            else:
                time.sleep(1) # Avoid api rate limit
                coordinates, source = self.geocode_address(destination["address"])
                if coordinates is None:
                    has_null_coordiantes_names.append(destination["name"])
            result.append({
                "name": destination["name"],
                "address": destination["address"],
                "count": destination["count"],
                "Source": source,
                "coordinates": coordinates
            })

        if has_null_coordiantes_names:
            print(f"Some addresses are NULL and should be fixed manually: {has_null_coordiantes_names}")

        return result, not has_null_coordiantes_names
    
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
    print(f"{address}:{geocoder.geocode_usig(address)}")

    address = "MONTEVIDEO 937"
    print(f"{address}:{geocoder.geocode_address(address)}")
    print(f"{address}:{geocoder.geocode_usig(address)}")
