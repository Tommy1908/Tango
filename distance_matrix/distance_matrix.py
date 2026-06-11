import numpy as np

def build_distance_matrix_manhattan(coords, multiplier: float = 1) -> np.ndarray:
    coords_rad = np.radians(coords)
    lats = coords_rad[:, 0]
    lons = coords_rad[:, 1]
    
    dlat = lats[:, np.newaxis] - lats[np.newaxis, :]
    dlon = lons[:, np.newaxis] - lons[np.newaxis, :]
    
    mean_lat = (lats[:, np.newaxis] + lats[np.newaxis, :]) / 2.0
    R = 6371000  
    x = dlon * np.cos(mean_lat)
    y = dlat
    
    meter_matrix = R * (np.abs(x) + np.abs(y))
    meter_matrix = meter_matrix * multiplier
    
    return np.round(meter_matrix).astype(np.int32)