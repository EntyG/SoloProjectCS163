import json
from re import S

pathKeys = ["lat", "lng", "RouteId", "RouteVarId"]

class Path: 
    def __init__(self, path):
        for key, value in path.items():
            setattr(self, key, value)

    def setProperty(self, key, value):
        setattr(self, key, value)

    def getProperty(self, key):
        return getattr(self, key)
    
class PathQuery:
    def __init__(self):
        self._paths = []
            
    def addPath(self, path):
        self._paths.append(path)

    def getPaths(self):
        return self._paths
    
    def readJSONInput(self, file_name):
        with open(file_name, 'r') as f:
            for line in f:
                path_data = json.loads(line)
                path = Path(path_data)
                self.addPath(path)
    
    def outputAsCSV(self, file_name):
        with open(file_name, 'w') as f:
           f.write(",".join(pathKeys) + "\n")
           for i in self._paths:
               path_values = [str(i.getProperty(key)) for key in pathKeys]
               f.write(",".join(path_values) + "\n")
                
    def outputAsJSON(self, file_name):
        with open(file_name, 'w') as f:
            for i in self._paths:
                text = json.dumps(i, default=lambda o: o.__dict__, ensure_ascii=False)
                f.write(text + "\n")
       
import pyproj

wgs84_crs = pyproj.CRS("EPSG:4326")
utm_vn_crs = pyproj.CRS("EPSG:3405")
transformer_to_utm = pyproj.Transformer.from_proj(wgs84_crs, utm_vn_crs, always_xy=True)
transformer_to_wgs84 = pyproj.Transformer.from_proj(utm_vn_crs, wgs84_crs, always_xy=True)

def LngLat_To_XY(Lng, Lat):
    if Lng is None or Lat is None:
        return None, None
    x, y = transformer_to_utm.transform(Lng, Lat)
    return x, y
   
def XY_To_LngLat(x, y):
    if x is None or y is None:
        return None, None
    Lng, Lat = transformer_to_wgs84.transform(x, y)
    return Lng, Lat
            
def almostEqual(a, b, epsilon=1e-4):
    return abs(a - b) < epsilon

def distance(source_path, stop1, stop2):
    lng1 = stop1.getProperty("Lng")
    lat1 = stop1.getProperty("Lat")
    lng2 = stop2.getProperty("Lng")
    lat2 = stop2.getProperty("Lat")
    founded = False
    lats = source_path.getProperty("lat")
    lngs = source_path.getProperty("lng")
    
    res = 0.0
    for i in range(len(lats)):
        if founded:
            x_i, y_i = LngLat_To_XY(lngs[i - 1], lats[i - 1])
            x_f, y_f = LngLat_To_XY(lngs[i], lats[i])
            if None not in [x_i, y_i, x_f, y_f]:
                res += ((x_f-x_i)**2 + (y_f-y_i)**2)**0.5

        if almostEqual(lats[i], lat1) and  almostEqual(lngs[i], lng1):
            founded = True
        
        if  almostEqual(lats[i], lat2) and  almostEqual(lngs[i], lng2):
            break
    return res

if __name__ == "__main__":
    path_querry = PathQuery()
    path_querry.readJSONInput("paths.json")
    path_querry.outputAsJSON("test_paths.json")
