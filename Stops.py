import json

stopKeys = ["StopId", "Code", "Name", "StopType", "Zone", "Ward", "AddressNo", "Street", "SupportDisability", "Status", "Lng", "Lat", "Search", "Routes"]

class Stop: 
    def __init__(self, stops):
        for key, value in stops.items():
            setattr(self, key, value)
      
    def setProperty(self, key, value):
        setattr(self, key, value)

    def getProperty(self, key):
        return getattr(self, key)
    
class RouteStops:
    def __init__ (self, route_id, route_var_id):    
        self._route_stops = []
        self._route_id = route_id
        self._route_var_id = route_var_id
        
    @property
    def route_id(self):
        return self._route_id
    
    @property
    def route_var_id(self):
        return self._route_var_id
    
    def addStop(self, stop):
        if isinstance(stop, Stop):
            self._route_stops.append(stop)
        else:
            raise TypeError("Adding wrong instances to  RouteStops")

    def getStops(self):
        return self._route_stops

class StopsQuery:
    def __init__(self):
        self._stops_list = []

    def addStops(self, stops):
        if isinstance(stops, RouteStops):
            self._stops_list.append(stops)
        else:
            raise TypeError("Adding wrong instances to StopsQuerry")
        
    def getStopList(self):
        return self._stops_list
    
    def readJSONInput(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                route_stops_data = json.loads(line)
                route_stops = RouteStops(route_stops_data["RouteId"], route_stops_data["RouteVarId"])
                for stop_data in route_stops_data["Stops"]:
                    stop = Stop(stop_data)
                    route_stops.addStop(stop)
                self.addStops(route_stops)

    def outputAsCSV(self, file_name) -> None:
        with open(file_name, 'w', encoding="UTF-8") as f:
            f.write("RouteId,RouteVarId\n")
            f.write(",".join(stopKeys) + "\n")
            for route_stops in self._stops_list:
                f.write(",".join([str(route_stops._route_id), str(route_stops._route_var_id)]) + "\n")
                for stop in route_stops.getStops():
                    stop_values = [str(stop.getProperty(key)) for key in stopKeys]
                    f.write(",".join(stop_values) + "\n")  
         
    def outputAsJSON(self, file_name) -> None:
        with open(file_name, 'w', encoding="UTF-8") as f:
            for i in self._stops_list:
                text = json.dumps({
                    "Stops": [stop.__dict__ for stop in i._route_stops],
                    "RouteId": i._route_id,
                    "RouteVarId": i._route_var_id
                    }, default=lambda o: o.__dict__, ensure_ascii=False)
                f.write(text + "\n")

if __name__ == "__main__":
    stops_query = StopsQuery()
    stops_query.readJSONInput("stops.json")
    stops_query.outputAsJSON("test_stops.json")