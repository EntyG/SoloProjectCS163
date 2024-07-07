import json

routeKeys = ["RouteId", "RouteVarId", "RouteVarName", "RouteVarShortName", "RouteNo", "StartStop", "EndStop", "Distance", "Outbound", "RunningTime"]

class RouteVars:
    def __init__(self, routes):
        self.routeVar = routes + [None] * (2 - len(routes))
        self._len = len(routes)
          
    def setProperty(self, index, key, value):
        if index not in [0, 1]:
            raise IndexError("Index should be 0 or 1.")
        if self.routeVar[index] is None:
            self.routeVar[index] = {}
        self.routeVar[index][key] = value

    def __len__(self):
        return self._len

    def getProperty(self, index, key):
        if index not in [0, 1]:
            raise IndexError("Index should be 0 or 1.")
        if not self.routeVar[index]:
            return None
        return self.routeVar[index].get(key, None)
    
    def getRouteVar(self, index):
        if index not in [0, 1]:
            raise IndexError("Index should be 0 or 1.")
        return self.routeVar[index]

class RouteVarsQuery:
    def __init__(self):
        self._route_vars_list = []
        
    def addRouteVars(self, route_var):
        if isinstance(route_var, RouteVars) and (len(route_var) == 1 or len(route_var) == 2):
            self._route_vars_list.append(route_var)
        else:
            if not isinstance(route_var, RouteVars):
                raise TypeError("Adding wrong instances to RouteVarsQuery")
    
    def getRouteVars(self):
        return self._route_vars_list

    def readJSONInput(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                route_var_data_list = json.loads(line)
                route = RouteVars(route_var_data_list)
                self.addRouteVars(route)

    def outputAsCSV(self, file_name) -> None:
        with open(file_name, 'w', encoding="UTF-8") as f:
            f.write(",".join(routeKeys) + "\n")
            for route_var in self._route_vars_list:
                for i in range(2):
                   if route_var.getRouteVar(i) is not None:
                        route_values = [str(route_var.getProperty(i, key)) for key in routeKeys]
                        f.write(",".join(route_values) + "\n")
            
    def outputAsJSON(self, file_name) -> None:
        with open(file_name, 'w', encoding="UTF-8") as f:
            for pair_route_vars in self._route_vars_list:
                route_var1 = pair_route_vars.getRouteVar(0)
                route_var2 = pair_route_vars.getRouteVar(1)
                text = json.dumps(
                    [route_var1, route_var2]
                    , default=lambda o: o.__dict__, ensure_ascii=False)
                f.write(text + "\n")
  
if __name__ == "__main__":
    route_vars_query = RouteVarsQuery()
    route_vars_query.readJSONInput("vars.json")
    route_vars_query.outputAsCSV("test_vars.csv")

