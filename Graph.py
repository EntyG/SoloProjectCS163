from collections import defaultdict
import time
from Stops import *
from RouteVars import *
from Paths import *
import heapq
from math import inf
import sys
import threading
import os

class ProgressEvent:
    def __init__(self):
        self.completed_tasks = 0
        self.event = threading.Event()
        self.lock = threading.Lock()

    def set(self):
        self.event.set()

    def is_set(self):
        return self.event.is_set()

    def increment(self, value=1):
        with self.lock:
            self.completed_tasks += value

def print_progress_bar(progress_event, total_tasks, length=50):
    try:
        while not progress_event.is_set():
            with progress_event.lock:
                percentage = (progress_event.completed_tasks / total_tasks) * 100
                
            bar_length = int(length * (percentage / 100.0))
            bar = '█' * bar_length + '-' * (length - bar_length)
            
            sys.stdout.write(f'\r|{bar}| {percentage:.2f}% ')
            sys.stdout.flush()
            if progress_event.completed_tasks >= total_tasks:
                progress_event.set()
            time.sleep(1)
    except Exception as e:
        progress_event.set()
        sys.stdout.write(f'\nError occurred: {str(e)}\n')
    
    sys.stdout.write('\r|{}| 100.00%\n'.format('█' * length))

class Graph:
    def __init__(self):
        self._all_stops = {}
        self._all_coords = {}
        self._adj = defaultdict(list)
        self._incoming_edges = defaultdict(list)
        self._time_base_shortest_paths = defaultdict(list)
        self._distance_base_shortest_paths = defaultdict(list)
        self._zone = []
        self._in_zone_node = defaultdict(list)
        self._fixed_shortest_path = defaultdict(list)
        self._fixed_fastest_path = defaultdict(list)
        
    def reset(self):
        self._time_base_shortest_paths = {}
        self._distance_base_shortest_paths = {}

    def getListNodeData(self):
        return list(self._all_stops.values())

    def addNodeData(self, stop):
        if stop.getProperty("StopId") not in self._all_stops:
            self._all_stops[stop.getProperty("StopId")] = stop
            self._all_coords[stop.getProperty("StopId")] = LngLat_To_XY(stop.getProperty("Lng"), stop.getProperty("Lat"))
        
    def addEdge(self, from_node_id, to_node_id, distance_weight, time_weight, route_id, route_var_id):
        self._adj[from_node_id].append((to_node_id, distance_weight, time_weight, route_id, route_var_id))
        self._incoming_edges[to_node_id].append((from_node_id, distance_weight, time_weight, route_id, route_var_id))

    def getAdj(self, u):
        return self._adj[u]

    def getIncomingEdges(self, node_id):
        return self._incoming_edges[node_id]

    def getCoord(self, stop_id):
        return self._all_coords[stop_id]

    def divGraph(self):
        for stop in self.getListNodeData():
            if stop.getProperty("Zone") not in self._zone:
                self._zone.append(stop.getProperty("Zone"))
            self._in_zone_node[stop.getProperty("Zone")].append(stop.getProperty("StopId"))

    def pathCatchingPrecompute(self):
        self._fixed_shortest_path = {}
        self._fixed_fastest_path = {}
        
        total_tasks = len(self.getListNodeData()) * (len(self._zone) - 1)

        progress_event = ProgressEvent()
    
        progress_thread = threading.Thread(target=print_progress_bar, args=(progress_event, total_tasks))
        progress_thread.start()
        for stop in self.getListNodeData():
            src_zone = stop.getProperty("Zone")
            stop_id = stop.getProperty("StopId")
            self.dijkstraDistanceBase(stop_id)
            self.dijkstraTimeBase(stop_id)
            for zone in self._zone:
                if zone == src_zone:
                    continue
                fixed_shortest_path = self._fixed_shortest_path.get((src_zone, zone))
                dist = fixed_shortest_path[0][1] if fixed_shortest_path is not None else inf
                fixed_fastest_path = self._fixed_fastest_path.get((src_zone, zone))
                time = fixed_fastest_path[0][1] if fixed_fastest_path is not None else inf
                for stop_id2 in self._in_zone_node[zone]:
                    path = self.shortestPath(stop_id, stop_id2)
                    if path is not None and path[0][1] < dist:
                        dist = path[0][1]
                        fixed_shortest_path = path
                    path = self.fastestPath(stop_id, stop_id2)
                    if path is not None and path[0][1] < time:
                        time = path[0][1]
                        fixed_fastest_path = path
                self._fixed_shortest_path[(src_zone, zone)] = fixed_shortest_path
                self._fixed_fastest_path[(src_zone, zone)] = fixed_fastest_path
                progress_event.increment()
            self.reset()

        with open("fixed_paths.json", 'w', encoding = 'utf-8') as f:
            for zone1 in self._zone:
                for zone2 in self._zone:
                    if zone1 == zone2:
                        continue
                    f.write(json.dumps({
                        "Start": zone1, 
                        "End": zone2, 
                        "ShortestPath": self._fixed_shortest_path[(zone1, zone2)], 
                        "FastestPath": self._fixed_fastest_path[(zone1, zone2)]
                        }, default=lambda o: o.__dict__, ensure_ascii=False) + '\n')
        
        progress_event.set()
        progress_thread.join()
 
    def dijkstraDistanceBase(self, start_id):
        pq = [(0, start_id)]
        distances = {start_id: 0}
        parents = {start_id: (None, None, None)}

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_distance > distances[current_node]:
                continue

            for neighbor, distance_weight, time_weight, route_id, route_var_id in self.getAdj(current_node):
                distance = current_distance + distance_weight

                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    parents[neighbor] = (current_node, route_id, route_var_id)
                    heapq.heappush(pq, (distance, neighbor))

        # Store all paths from start_id to other nodes
        for node in distances:
            path = []
            current = node
            while current != start_id:
                parent, route_id, route_var_id = parents[current]
                path.insert(0, (current, route_id, route_var_id))
                current = parent
            path.insert(0, (start_id, distances.get(node)))
            if path:
                self._distance_base_shortest_paths[(start_id, node)] = path

    def shortestPath(self, start_id, goal_id):
        if (start_id, goal_id) not in self._distance_base_shortest_paths:
            self.dijkstraDistanceBase(start_id)
        return self._distance_base_shortest_paths.get((start_id, goal_id))
    
    def dijkstraTimeBase(self, start_id):
        pq = [(0, start_id)]
        time_costs = {start_id: 0}
        parents = {start_id: (None, None, None)}

        while pq:
            current_time_cost, current_node = heapq.heappop(pq)

            if current_time_cost > time_costs[current_node]:
                continue

            for neighbor, distance_weight, time_weight, route_id, route_var_id in self.getAdj(current_node):
                time_cost = current_time_cost + time_weight

                if neighbor not in time_costs or time_cost < time_costs[neighbor]:
                    time_costs[neighbor] = time_cost
                    parents[neighbor] = (current_node, route_id, route_var_id)
                    heapq.heappush(pq, (time_cost, neighbor))

        # Store all paths from start_id to other nodes
        for node in time_costs:
            path = []
            current = node
            while current != start_id:
                parent, route_id, route_var_id = parents[current]
                path.insert(0, (current, route_id, route_var_id))
                current = parent
            path.insert(0, (start_id, time_costs.get(node)))
            if path:
                self._time_base_shortest_paths[(start_id, node)] = path

    def fastestPath(self, start_id, goal_id):
        if (start_id, goal_id) not in self._time_base_shortest_paths:
            self.dijkstraTimeBase(start_id)
        return self._time_base_shortest_paths.get((start_id, goal_id))

    def aStarDistanceBase(self, start_id, goal_id):
        def euclidDistance(stop_id1, stop_id2):
            x1, y1 = self._all_coords[stop_id1]
            x2, y2 = self._all_coords[stop_id2]
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        
        pq = [(0, start_id)]
        distances = {start_id: 0}
        parents = {start_id: (None, None, None)}
        heuristic_cache = {}

        while pq:
            current_distance, current = heapq.heappop(pq)

            if current == goal_id:
                path = []
                current = goal_id
                while current != start_id:
                    parent, route_id, route_var_id = parents[current]
                    path.insert(0, (current, route_id, route_var_id))
                    current = parent
                path.insert(0, (start_id, distances.get(goal_id)))
                return path

            for neighbor, distance_weight, time_weight, route_id, route_var_id in self.getAdj(current):
                distance = distances[current] + distance_weight

                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    parents[neighbor] = (current, route_id, route_var_id)
                    if neighbor not in heuristic_cache:
                        heuristic_cache[neighbor] = euclidDistance(neighbor, goal_id)
                    priority = distances[neighbor] + heuristic_cache[neighbor]
                    heapq.heappush(pq, (priority, neighbor))

        return None
 
    def aStarTimeBase(self, start_id, goal_id):
        def euclidDistance(stop_id1, stop_id2):
            x1, y1 = self._all_coords[stop_id1]
            x2, y2 = self._all_coords[stop_id2]
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        
        pq = [(0, start_id)]
        distances = {start_id: 0}
        parents = {start_id: (None, None, None)}
        heuristic_cache = {}

        while pq:
            current_distance, current = heapq.heappop(pq)

            if current == goal_id:
                path = []
                current = goal_id
                while current != start_id:
                    parent, route_id, route_var_id = parents[current]
                    path.insert(0, (current, route_id, route_var_id))
                    current = parent
                path.insert(0, (start_id, distances.get(goal_id)))
                return path

            for neighbor, distance_weight, time_weight, route_id, route_var_id in self.getAdj(current):
                distance = distances[current] + time_weight

                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    parents[neighbor] = (current, route_id, route_var_id)
                    if neighbor not in heuristic_cache:
                        heuristic_cache[neighbor] = euclidDistance(neighbor, goal_id)
                    priority = distances[neighbor] + heuristic_cache[neighbor]
                    heapq.heappush(pq, (priority, neighbor))

        return None      
   
    def shortestPathWithCache(self, start_id, goal_id):
        zone1 = self._all_stops[start_id].getProperty("Zone")
        zone2 = self._all_stops[goal_id].getProperty("Zone")
        if zone1 == zone2:
            return self.shortestPath(start_id, goal_id)
        if (zone1, zone2) not in self._fixed_shortest_path:
            return self.shortestPath(start_id, goal_id)
        if self._fixed_shortest_path[(zone1, zone2)] is None:
            return self.shortestPath(start_id, goal_id)
        
        fixed_point_in_zone1 = self._fixed_shortest_path[(zone1, zone2)][0][0]
        fixed_point_in_zone2 = self._fixed_shortest_path[(zone1, zone2)][len(self._fixed_shortest_path[(zone1, zone2)]) - 1][0]
        path_in_zone1 = self.aStarDistanceBase(start_id, fixed_point_in_zone1)
        if path_in_zone1 is None:
            return self.shortestPath(start_id, goal_id)
        fixed_path = self._fixed_shortest_path[(zone1, zone2)][1:]
        path2 = self.aStarDistanceBase(fixed_point_in_zone2, goal_id)
        if path2 is None:
            return self.shortestPath(start_id, goal_id)
        path_in_zone2 = path2[1:]
        path_in_zone1[0] = (start_id, path_in_zone1[0][1] + self._fixed_shortest_path[(zone1, zone2)][0][1] + path2[0][1])
        return path_in_zone1 + fixed_path + path_in_zone2
    
    def fastestPathWithCache(self, start_id, goal_id):
        zone1 = self._all_stops[start_id].getProperty("Zone")
        zone2 = self._all_stops[goal_id].getProperty("Zone")
        if zone1 == zone2:
            return self.fastestPath(start_id, goal_id)
        if (zone1, zone2) not in self._fixed_fastest_path:
            return self.fastestPath(start_id, goal_id)
        if self._fixed_fastest_path[(zone1, zone2)] is None:
            return self.fastestPath(start_id, goal_id)
        
        fixed_point_in_zone1 = self._fixed_fastest_path[(zone1, zone2)][0][0]
        fixed_point_in_zone2 = self._fixed_fastest_path[(zone1, zone2)][len(self._fixed_fastest_path[(zone1, zone2)]) - 1][0]
        path_in_zone1 = self.aStarTimeBase(start_id, fixed_point_in_zone1)
        if path_in_zone1 is None:
            return self.fastestPath(start_id, goal_id)
        fixed_path = self._fixed_fastest_path[(zone1, zone2)][1:]
        path2 = self.aStarTimeBase(fixed_point_in_zone2, goal_id)
        if path2 is None:
            return self.fastestPath(start_id, goal_id)
        path_in_zone2 = path2[1:]
        path_in_zone1[0] = (start_id, path_in_zone1[0][1] + self._fixed_fastest_path[(zone1, zone2)][0][1] + path2[0][1])
        return path_in_zone1 + fixed_path + path_in_zone2

    def buildGraph(self, stops_file, route_vars_file, paths_file, fixed_path_file = None):
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
        self.divGraph()
        if fixed_path_file is not None and os.path.exists(fixed_path_file) and os.path.getsize(fixed_path_file) > 0:
            with open(fixed_path_file, 'r', encoding = 'utf-8') as f:
                for line in f:
                    fixed_path = json.loads(line)
                    self._fixed_shortest_path[(fixed_path["Start"], fixed_path["End"])] = fixed_path["ShortestPath"]
                    self._fixed_fastest_path[(fixed_path["Start"], fixed_path["End"])] = fixed_path["FastestPath"]
        else:
            self.pathCatchingPrecompute()
        
if __name__ == "__main__":
  graph = Graph()
        