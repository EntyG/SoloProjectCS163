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
    
class PathQuerry:
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
        
if __name__ == "__main__":
    path_querry = PathQuerry()
    path_querry.readJSONInput("paths.json")
    path_querry.outputAsJSON("test_paths.json")
