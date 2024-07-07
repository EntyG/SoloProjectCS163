import json

routeKeys = ["RouteId", "RouteVarId", "RouteVarName", "RouteVarShortName", "RouteNo", "StartStop", "EndStop", "Distance", "Outbound", "RunningTime"]

class RouteVars:
    def __init__(self, routes):
        if len(routes) != 2:
            raise ValueError("RouteVars should consist of exactly two routes.")
        self.routeVar = routes
          
    def setProperty(self, index, key, value):
        if index not in [0, 1]:
            raise IndexError("Index should be 0 or 1.")
        self.routeVar[index][key] = value

    def getProperty(self, index, key):
        if index not in [0, 1]:
            raise IndexError("Index should be 0 or 1.")
        return self.routeVar[index][key]
    
    def get_route_vars(self, index):
        return self.routeVar[index]

class RouteVarsQuery:
    def __init__(self):
        self._route_vars_list = []
        
    def add_route_var(self, route_var):
        if isinstance(route_var, RouteVars):
            self._route_vars_list.append(route_var)
        else:
            raise TypeError("Adding wrong instances to RouteVarsQuery")
    
    def get_route_vars(self):
        return self._route_vars_list

    def outputAsCSV(self, file_name) -> None:
        with open(file_name, 'w', encoding="UTF-8") as f:
            f.write(",".join(routeKeys) + "\n")
            for route_var in self._route_vars_list:
                for i in range(2):
                    route_values = [str(route_var.getProperty(i, key)) for key in routeKeys]
                    f.write(",".join(route_values) + "\n")
            
    def outputAsJSON(self, file_name) -> None:
        with open(file_name, 'w', encoding="UTF-8") as f:
            for pair_route_vars in self._route_vars_list:
                route_var1 = pair_route_vars.get_route_vars(0)
                route_var2 = pair_route_vars.get_route_vars(1)
                text = json.dumps(
                    [route_var1, route_var2]
                    , default=lambda o: o.__dict__, ensure_ascii=False)
                f.write(text + "\n")
  
if __name__ == "__main__":
    route_var_data1 = {
        "RouteId": 1,
        "RouteVarId": 1,
        "RouteVarName": "Lượt đi: Bến Thành - BX Chợ Lớn",
        "RouteVarShortName": "Bến Xe buýt Chợ Lớn",
        "RouteNo": "01",
        "StartStop": "Công Trường Mê Linh",
        "EndStop": "Bến xe Chợ Lớn",
        "Distance": 8381.0,
        "Outbound": True,
        "RunningTime": 35
    }

    route_var_data2 = {
        "RouteId": 1,
        "RouteVarId": 2,
        "RouteVarName": "Lượt về: BX Chợ Lớn - Bến Thành",
        "RouteVarShortName": "Bến Thành",
        "RouteNo": "01",
        "StartStop": "Bến xe Chợ Lớn",
        "EndStop": "Công Trường Mê Linh",
        "Distance": 9458.0,
        "Outbound": False,
        "RunningTime": 35
    }

    route_var_data3 = {
        "RouteId": 3,
        "RouteVarId": 5,
        "RouteVarName": "Lượt đi: Bến Thành - Thạnh Lộc",
        "RouteVarShortName": "Thạnh Lộc",
        "RouteNo": "03",
        "StartStop": "Bến xe buýt Sài Gòn",
        "EndStop": "THẠNH LỘC",
        "Distance": 21456.0,
        "Outbound": True,
        "RunningTime": 70
    }

    route_var_data4 = {
        "RouteId": 3,
        "RouteVarId": 6,
        "RouteVarName": "Lượt về: Thạnh Lộc - Bến Thành",
        "RouteVarShortName": "Bến Thành",
        "RouteNo": "03",
        "StartStop": "THẠNH LỘC",
        "EndStop": "Bến xe buýt Sài Gòn",
        "Distance": 21704.0,
        "Outbound": False,
        "RunningTime": 70
    }

    route_var1 = RouteVars([route_var_data1, route_var_data2])
    route_var2 = RouteVars([route_var_data3, route_var_data4])

    route_vars_query = RouteVarsQuery()
    route_vars_query.add_route_var(route_var1)
    route_vars_query.add_route_var(route_var2)
