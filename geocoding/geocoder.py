from geopy.geocoders import Photon, Nominatim
from geopy.location import Location
from typing import Any, cast

class Geocoder:
    def __init__(self):
        self.geolocator = Photon(timeout=5)

    def geocode_address(self, address:str, city="Ciudad Autónoma de Buenos Aires", country="Argentina") -> tuple[float,float]:
    
        query = f"{address}, {city}, {country}"

        try:
            location = cast(Any, self.geolocator.geocode(query))
            if location:
                return (round(location.latitude, 7), round(location.longitude, 7))
        except Exception as e:
            print(f"API error (Photon): {e}")

        return (0.0, 0.0)


if __name__ == "__main__": # pragma: no cover
    address = "ARENALES 1210"
    geocoder = Geocoder()
    print(f"{address}:{geocoder.geocode_address(address)}")

    address = "MONTEVIDEO 937"
    geocoder = Geocoder()
    print(f"{address}:{geocoder.geocode_address(address)}")
