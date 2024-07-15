from math import inf
import json
import time
import threading
import sys
from Graph import Graph
import random

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

def print_progress_bar(progress_event, total_tasks, start_time, length=50):
    try:
        while not progress_event.is_set():
            with progress_event.lock:
                percentage = (progress_event.completed_tasks / total_tasks) * 100
                elapsed_time = time.time() - start_time
                tasks_per_second = progress_event.completed_tasks / elapsed_time if elapsed_time > 0 else 0
                remaining_tasks = total_tasks - progress_event.completed_tasks
                estimated_remaining_time = remaining_tasks / tasks_per_second if tasks_per_second > 0 else 0
                
            bar_length = int(length * (percentage / 100.0))
            bar = '█' * bar_length + '-' * (length - bar_length)
            
            sys.stdout.write(f'\r|{bar}| {percentage:.2f}% '
                             f'Elapsed: {elapsed_time:.2f}s '
                             f'Remaining: {estimated_remaining_time:.2f}s')
            sys.stdout.flush()
            if progress_event.completed_tasks >= total_tasks:
                progress_event.set()
            time.sleep(1)
    except Exception as e:
        progress_event.set()
        sys.stdout.write(f'\nError occurred: {str(e)}\n')

    sys.stdout.write('\r|{}| 100.00%\n'.format('█' * length))

#store data take 40m, non storing take 10m
def allPairs():  
    start = time.time()
    graph = Graph()
    graph.buildGraph("stops.json", "vars.json", "paths.json")
    max_time = 0
    min_time = inf

    list_stop = graph.getListNodeData()
    n = len(list_stop)
    total_tasks = n * (n - 1)
    
    list_stop_id = [stop.getProperty("StopId") for stop in list_stop]

    progress_event = ProgressEvent()
    
    progress_thread = threading.Thread(target=print_progress_bar, args=(progress_event, total_tasks, start))
    progress_thread.start()
    
    for i in range(n):
        start_id = list_stop_id[i]
        graph.dijkstraDistanceBase(start_id)
        graph.dijkstraTimeBase(start_id)
        for j in range(n):
            if i == j:
                continue
            goal_id = list_stop_id[j]
            shortest_path = graph.shortestPath(start_id, goal_id)
            fastest_path = graph.fastestPath(start_id, goal_id)
                    
            progress_event.increment()
        graph.reset()

    end = time.time()
    
    progress_event.set()
    progress_thread.join()

    print(f"Total time cost: {end - start}")

def storeAllPairs(file_name):
    start = time.time()
    graph = Graph()
    graph.buildGraph("stops.json", "vars.json", "paths.json")
    max_time = 0
    min_time = inf

    list_stop = graph.getListNodeData()
    n = len(list_stop)
    total_tasks = n * (n - 1)
    
    list_stop_id = [stop.getProperty("StopId") for stop in list_stop]

    progress_event = ProgressEvent()
    
    progress_thread = threading.Thread(target=print_progress_bar, args=(progress_event, total_tasks, start))
    progress_thread.start()
    
    with open(file_name, 'w') as f:
        for i in range(n):
            start_id = list_stop_id[i]
            graph.dijkstraDistanceBase(start_id)
            graph.dijkstraTimeBase(start_id)
            for j in range(n):
                if i == j:
                    continue
                goal_id = list_stop_id[j]
                shortest_path = graph.shortestPath(start_id, goal_id)
                fastest_path = graph.fastestPath(start_id, goal_id)
                text = json.dumps({
                    "Start": start_id,
                    "Goal": goal_id,
                    "ShortestPath": shortest_path,
                }, default=lambda o: o.__dict__, ensure_ascii=False)
                f.write(text + '\n')

                progress_event.increment()
            graph.reset()

    end = time.time()
    
    progress_event.set()
    progress_thread.join()

    print(f"Total time cost: {end - start}")

def measure_algorithm_performance(num_tests, stops_file, vars_file, paths_file, fixed_paths_file = None):
    graph = Graph()
    graph.buildGraph(stops_file, vars_file, paths_file, fixed_paths_file)

    stops_list = graph.getListNodeData()
    stop_ids = [stop.getProperty('StopId') for stop in stops_list]
    
    def measure_time(func):
        total_time = 0.0
        pairs = list() 
        for _ in range(num_tests):
            start_id, goal_id = random.sample(stop_ids, 2)
            pairs.append((start_id, goal_id))
        pairs = sorted(pairs, key=lambda x: x[0])
        current_start = pairs[0][0]
        for start_id, goal_id in pairs:
            if start_id != current_start:
                graph.reset()
                current_start = start_id
            start_time = time.time()
            func(start_id, goal_id)
            total_time += time.time() - start_time
        return total_time / num_tests

    print("Shortest path finding algorithm performance:")

    # Measure average running time of Dijkstra's distance-based algorithm
    avg_dijkstra_distance_time = measure_time(graph.shortestPath)
    print(f'Average running time of Dijkstra: {avg_dijkstra_distance_time:.6f} seconds')

    # Measure average running time of A* distance-based algorithm
    avg_astar_distance_time = measure_time(graph.aStarDistanceBase)
    print(f'Average running time of A*: {avg_astar_distance_time:.6f} seconds')

    # Measure average running time of shortest path with cache
    avg_path_caching_shortest_time = measure_time(graph.shortestPathWithCache)
    print(f'Average running time of path caching combine with A*: {avg_path_caching_shortest_time:.6f} seconds')

    print("Fastest path finding algorithm performance:") 

    # Measure average running time of Dijkstra's time-based algorithm
    avg_dijkstra_time_time = measure_time(graph.fastestPath)
    print(f'Average running time of Dijkstra: {avg_dijkstra_time_time:.6f} seconds')

    # Measure average running time of A* time-based algorithm
    avg_astar_time_time = measure_time(graph.aStarTimeBase)
    print(f'Average running time of A*: {avg_astar_time_time:.6f} seconds')

    # Measure average running time of fastest path with cache
    avg_path_caching_fastest_time = measure_time(graph.fastestPathWithCache)
    print(f'Average running time of path caching combine with A*: {avg_path_caching_fastest_time:.6f} seconds')
    
if __name__ == "__main__":
    measure_algorithm_performance(1000, "stops.json", "vars.json", "paths.json", "fixed_paths.json")