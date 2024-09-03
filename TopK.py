import pandas as pd
from collections import defaultdict
import heapq
import sys

class BusStopNode:
    def __init__(self, route_id, var_id, stop_id, timestamp, node_type, latx, lngy):
        self.route_id = route_id
        self.var_id = var_id
        self.stop_id = stop_id
        self.timestamp = timestamp
        self.node_type = node_type
        self.latx = latx
        self.lngy = lngy

class Edge:
    def __init__(self, end_stop_id, transfers, travel_time):
        self.end_stop_id = end_stop_id
        self.transfers = transfers
        self.travel_time = travel_time

def load_data(file_path):
    data = pd.read_csv(file_path, header=None)
    # Convert timestamps from seconds to datetime
    data[3] = pd.to_datetime(data[3], unit='s')
    data[7] = pd.to_datetime(data[7], unit='s')
    return data

class Graph:
    def __init__(self):
        self.adjacency_list = defaultdict(list)
        self.stops = {}
        self.shortest_paths = defaultdict(list)

    def reset(self):
        self.shortest_paths = defaultdict(list)

    def add_stop(self, bus_stop_node):
        self.stops[bus_stop_node.stop_id] = bus_stop_node

    def add_edge(self, start_stop_id, end_stop_id, transfers, travel_time):
        edge = Edge(end_stop_id, transfers, travel_time)
        self.adjacency_list[start_stop_id].append(edge)

    def get_neighbors(self, stop_id):
        return self.adjacency_list[stop_id]

    def dijkstra(self, start_stop_id):
        pq = [(0, start_stop_id)]
        distances = {start_stop_id: 0}
        parents = {start_stop_id: (None, None)}

        while pq:
            current_distance, current_stop_id = heapq.heappop(pq)

            if current_distance > distances[current_stop_id]:
                continue

            for edge in self.get_neighbors(current_stop_id):
                neighbor_stop_id = edge.end_stop_id
                distance = current_distance + edge.travel_time

                if neighbor_stop_id not in distances or distance < distances[neighbor_stop_id]:
                    distances[neighbor_stop_id] = distance
                    parents[neighbor_stop_id] = (current_stop_id, edge.transfers)
                    heapq.heappush(pq, (distance, neighbor_stop_id))

        # Store all paths from start_stop_id to other nodes
        for stop_id in distances:
            path = []
            current = stop_id
            while current != start_stop_id:
                parent, transfers = parents[current]
                path.insert(0, (current, transfers))
                current = parent
            path.insert(0, (start_stop_id, distances[stop_id]))
            if path:
                self.shortest_paths[(start_stop_id, stop_id)] = path

def calculate_all_pairs_shortest_paths(graph):
    n = len(graph.stops)
    cnt = 0
    stop_importance = defaultdict(int)

    for stop_id in graph.stops:
        graph.dijkstra(stop_id)
        cnt+=1
        print(f"Calculating shortest paths for stop {cnt}/{n}")
        for stop_id_2 in graph.stops:
            if stop_id_2 != stop_id:
                path = graph.shortest_paths.get((stop_id, stop_id_2), [])
                for node, transfers in path:
                    stop_importance[node] += 1
        graph.reset()
    return stop_importance


def build_graph(data):
    graph = Graph()
    for _, row in data.iterrows():
        start_node = BusStopNode(
            row[1], row[2], row[0], row[3], row[14], row[9], row[10]
        )
        end_node = BusStopNode(
            row[5], row[6], row[4], row[7], row[15], row[11], row[12]
        )

        graph.add_stop(start_node)
        graph.add_stop(end_node)

        transfers = 0 if row[1] == row[5] else 1
        travel_time = row[8]

        graph.add_edge(start_node.stop_id, end_node.stop_id, transfers, travel_time)
    return graph

def get_top_k_stops(stop_importance, k):
    top_k_stops = sorted(stop_importance.items(), key=lambda x: x[1], reverse=True)[:k]
    return top_k_stops

import time

def analyze_runtime():
    # Measure the runtime of each phase of the program

    # 1. Data Loading Phase
    start_time = time.time()
    data_type12 = load_data('type12.csv')
    data_type34 = load_data('type34.csv')
    data_loading_time = time.time() - start_time
    print(f"Data loading time: {data_loading_time:.4f} seconds")
    
    # 2. Graph Building Phase
    start_time = time.time()
    graph = build_graph(data_type12)
    graph = build_graph(data_type34)
    graph_building_time = time.time() - start_time
    print(f"Graph building time: {graph_building_time:.4f} seconds")

    # 3. Shortest Path Calculation Phase
    start_time = time.time()
    stop_importance = calculate_all_pairs_shortest_paths(graph)
    shortest_paths_time = time.time() - start_time
    print(f"Shortest path calculation time: {shortest_paths_time:.4f} seconds")
    
    # 4. Top k Stops Calculation Phase
    k = 5
    start_time = time.time()
    top_k_stops = get_top_k_stops(stop_importance, k)
    top_k_calculation_time = time.time() - start_time
    print(f"Top {k} stops calculation time: {top_k_calculation_time:.4f} seconds")

    # Summary
    total_runtime = data_loading_time + graph_building_time + shortest_paths_time + top_k_calculation_time
    print(f"Total runtime: {total_runtime:.4f} seconds")

    return {
        "data_loading_time": data_loading_time,
        "graph_building_time": graph_building_time,
        "shortest_paths_time": shortest_paths_time,
        "top_k_calculation_time": top_k_calculation_time,
        "total_runtime": total_runtime
    }

# Call the runtime analysis function
runtime_stats = analyze_runtime()
