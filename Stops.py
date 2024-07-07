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
        
    def add_stop(self, stop):
        if isinstance(stop, Stop):
            self._route_stops.append(stop)
        else:
            raise TypeError("Adding wrong instances to  RouteStops")

    def get_stops(self):
        return self._route_stops

class StopsQuery:
    def __init__(self):
        self._stops_list = []

    def add_stops(self, stops):
        if isinstance(stops, RouteStops):
            self._stops_list.append(stops)
        else:
            raise TypeError("Adding wrong instances to StopsQuerry")
        
    def get_stop_list(self):
        return self._stops_list

    def outputAsCSV(self, file_name) -> None:
        with open(file_name, 'w', encoding="UTF-8") as f:
            f.write("RouteId,RouteVarId\n")
            f.write(",".join(stopKeys) + "\n")
            for route_stops in self._stops_list:
                f.write(",".join([str(route_stops._route_id), str(route_stops._route_var_id)]) + "\n")
                for stop in route_stops.get_stops():
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
    stop_data1 = {
        "StopId": 35,
        "Code": "BX 01",
        "Name": "Bến xe buýt Sài Gòn",
        "StopType": "Bến xe",
        "Zone": "Quận 1",
        "Ward": "Phường Phạm Ngũ Lão",
        "AddressNo": "BẾN XE BUÝT SÀI GÒN",
        "Street": "Lê Lai",
        "SupportDisability": "Có",
        "Status": "Đang khai thác",
        "Lng": 106.689362,
        "Lat": 10.767676,
        "Search": "BxbSG BXBSG LL",
        "Routes": "03, 04, 102, 109, 120, 13, 140, 18, 19, 20, 27, 28, 34, 36, 39, 52, 61-6, 65, 69, 70-3, 72, 75, 86, 88, 93, D1"
    }

    stop_data2 = {
        "StopId": 36,
        "Code": "BX 02",
        "Name": "Bến xe buýt Hà Nội",
        "StopType": "Bến xe",
        "Zone": "Quận 2",
        "Ward": "Phường Tràng Tiền",
        "AddressNo": "BẾN XE BUÝT HÀ NỘI",
        "Street": "Phố Huế",
        "SupportDisability": "Có",
        "Status": "Đang khai thác",
        "Lng": 106.698162,
        "Lat": 10.776786,
        "Search": "BxbHN BXHN PH",
        "Routes": "01, 05, 103, 110, 121, 14, 141, 19, 29, 37, 39, 53, 62-6, 66, 71, 76, 89, 94, D2"
    }

    stop1 = Stop(stop_data1)
    stop2 = Stop(stop_data2)

    route_stops1 = RouteStops(1, 1)
    route_stops1.add_stop(stop1)
    route_stops1.add_stop(stop2)

    route_stops2 = RouteStops(1, 2)
    route_stops2.add_stop(stop2)
    route_stops2.add_stop(stop1)

    stops_querry = StopsQuery()
    stops_querry.add_stops(route_stops1)
    stops_querry.add_stops(route_stops2)