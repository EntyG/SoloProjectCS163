from collections import defaultdict 

class Graph:
    def __init__(self):
        self._all_coord = {}
        self._adj = defaultdict(list)
        
    def add_node_data(self, x, y, stop_id):
        self._all_coord[stop_id] = (x, y)
        
    def add_edge(self, from_node_id, to_node_id, weight, route_id, route_var_id):
        self._adj[from_node_id].append((to_node_id, weight, route_id, route_var_id))
        
    def get_adj(self, u):
        return self._adj[u]
    
    def get_coord(self, stop_id):
        return self._all_coord[stop_id]
    
    def a_star(self, start_id, goal_id):
        def euclid_distance(stop_id1, stop_id2):
            x1, y1 = self.get_coord(stop_id1)
            x2, y2 = self.get_coord(stop_id2)
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        
        open_list = set([start_id])
        distances = {start_id: 0};
        parents = {start_id: (None, None, None)}
    
        while open_list:
            current = min(open_list, key=lambda node_id: distances[node_id] + euclid_distance(node_id, goal_id))
            open_list.remove(current)
            if (current == goal_id):
                 break
        
            for neighbor, weight, route_id, route_var_id in self.get_adj(current):
                new_distance = distances[current] + weight
                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    parents[neighbor] = (current, route_id, route_var_id)
                    open_list.add(neighbor)
    
        path = []
        current = goal_id
        while current:
            parent, route_id, route_var_id = parents[current]
            path.insert(0, (current, route_id, route_var_id))
            current = parent
        return path
    
    def build_graph(self, input_stops_file, input_vars_file, input_paths_file):
        
    
if __name__ == "__main__":
    graph = Graph()
    graph.add_node_data(10, 10, 1)
    graph.add_node_data(20, 20, 2)
    graph.add_node_data(30, 30, 3)
    graph.add_node_data(40, 40, 4)
    graph.add_node_data(50, 50, 5)
    graph.add_edge(1, 2, 10, 1, 2)
    graph.add_edge(2, 3, 10, 1, 2)
    graph.add_edge(3, 4, 10, 3, 1)
    graph.add_edge(4, 5, 10, 4, 1)
    graph.add_edge(1, 3, 14, 2, 1)
    graph.add_edge(3, 5, 14, 5, 1)
    print(graph.a_star(1, 5))
        