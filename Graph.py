from collections import defaultdict
import time
from Stops import *
from RouteVars import *
from Paths import *

class Graph:
    def __init__(self):
        self._all_stops = {}
        self._adj = defaultdict(list)
        
    def getListNodeData(self):
        return list(self._all_stops.values())

    def addNodeData(self, stop):
        if stop.getProperty("StopId") not in self._all_stops:
            self._all_stops[stop.getProperty("StopId")] = stop
        
    def addEdge(self, from_node_id, to_node_id, distance_weight, time_weight, route_id, route_var_id):
        self._adj[from_node_id].append((to_node_id, distance_weight, time_weight, route_id, route_var_id))
        
    def getAdj(self, u):
        return self._adj[u]
    
    def getCoord(self, stop_id):
        return LngLat_To_XY(self._all_stops[stop_id].getProperty("Lng"), self._all_stops[stop_id].getProperty("Lat"))
    
    def aStarDistanceBase(self, start_id, goal_id):
        def euclidDistance(stop_id1, stop_id2):
            x1, y1 = self.getCoord(stop_id1)
            x2, y2 = self.getCoord(stop_id2)
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        
        open_list = set([start_id])
        distances = {start_id: 0};
        parents = {start_id: (None, None, None)}
    
        while open_list:
            current = min(open_list, key=lambda node_id: distances[node_id] + euclidDistance(node_id, goal_id))
            open_list.remove(current)
            if (current == goal_id):
                path = []
                current = goal_id
                while current:
                    parent, route_id, route_var_id = parents[current]
                    path.insert(0, (current, route_id, route_var_id))
                    current = parent
                return path
        
            for neighbor, distance_weight, time_weight, route_id, route_var_id in self.getAdj(current):
                new_distance = distances[current] + distance_weight
                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    parents[neighbor] = (current, route_id, route_var_id)
                    open_list.add(neighbor)
        return None
    
      
    
    def aStarTimeBase(self, start_id, goal_id):
        #Haven't found different heuristic function
        def euclidDistance(stop_id1, stop_id2):
            x1, y1 = self.getCoord(stop_id1)
            x2, y2 = self.getCoord(stop_id2)
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        
        open_list = set([start_id])
        time_cost = {start_id: 0};
        parents = {start_id: (None, None, None)}
    
        while open_list:
            current = min(open_list, key=lambda node_id: time_cost[node_id] + euclidDistance(node_id, goal_id))
            open_list.remove(current)
            if (current == goal_id):
                path = []
                current = goal_id
                while current:
                    parent, route_id, route_var_id = parents[current]
                    path.insert(0, (current, route_id, route_var_id))
                    current = parent
                return path
        
            for neighbor, distance_weight, time_weight, route_id, route_var_id in self.getAdj(current):
                new_time_cost = time_cost[current] + time_weight
                if neighbor not in time_cost or new_time_cost < time_cost[neighbor]:
                    time_cost[neighbor] = new_time_cost
                    parents[neighbor] = (current, route_id, route_var_id)
                    open_list.add(neighbor)
        return None      
   
    def buildGraph(self, stops_file, route_vars_file, paths_file):
        stops_query = StopsQuery()
        stops_query.readJSONInput(stops_file)
        route_vars_query = RouteVarsQuery()
        route_vars_query.readJSONInput(route_vars_file)
        path_query = PathQuery()
        path_query.readJSONInput(paths_file)
        n = len(stops_query.getStopList())
        for i in range(n):
            route_stops = stops_query.getStopList()[i]
            route_id = route_stops.route_id
            route_var_id = route_stops.route_var_id
            running_time = 0
            total_distance = 0.0
            
            founded = False
            for route_vars in route_vars_query.getRouteVars():
                for idx in range(2):
                    source_route_id = route_vars.getProperty(idx, "RouteId")
                    source_route_var_id = route_vars.getProperty(idx, "RouteVarId")
                    if source_route_id is not None and source_route_var_id is not None and int(source_route_id) == int(route_id) and int(source_route_var_id) == int(route_var_id):
                        running_time = route_vars.getProperty(idx, "RunningTime")
                        total_distance = route_vars.getProperty(idx, "Distance")
                        founded = True
                        break
                if founded:
                    break
                    
            path = path_query.getPaths()[i]
            for source_path in path_query.getPaths():
                if source_path.getProperty("RouteId") == route_id and source_path.getProperty("RouteVarId") == route_var_id:
                    path = source_path
            
            for j in range(len(route_stops.getStops()) - 1):
                f_stop = route_stops.getStops()[j]
                s_stop = route_stops.getStops()[j + 1]
                self.addNodeData(f_stop)
                self.addNodeData(s_stop)
                distance_weight = distance(path, f_stop, s_stop)
                time_weight = (running_time / total_distance) * distance_weight
                self.addEdge(f_stop.getProperty("StopId"), s_stop.getProperty("StopId"), distance_weight, time_weight, route_id, route_var_id)
 
if __name__ == "__main__":
  graph = Graph()
        