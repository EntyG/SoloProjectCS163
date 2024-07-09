from math import inf
import time
import threading
import sys
from Graph import Graph

class ProgressEvent:
    def __init__(self):
        self.completed_tasks = 0
        self.event = threading.Event()

    def is_set(self):
        return self.event.is_set()

    def set(self):
        self.event.set()

def print_progress_bar(progress_event, total_tasks, length=50):
    """Prints a progress bar of a given length for the specified duration."""
    while not progress_event.is_set():
        percentage = (progress_event.completed_tasks / total_tasks) * 100
        bar_length = int(length * (percentage / 100.0))
        bar = '█' * bar_length + '-' * (length - bar_length)
        sys.stdout.write(f'\r|{bar}| {percentage:.2f}%')
        sys.stdout.flush()
        if progress_event.completed_tasks >= total_tasks:
            progress_event.set()
        time.sleep(1)

    sys.stdout.write('\r|{}| 100.00%\n'.format('█' * length))

if __name__ == "__main__":
    start = time.time()
    graph = Graph()
    graph.buildGraph("stops.json", "vars.json", "paths.json")
    max_time = 0
    min_time = inf
    max_time_pair = ()
    min_time_pair = ()

    list_stop = graph.getListNodeData()
    total_tasks = len(list_stop) * (len(list_stop) - 1)
    
    progress_event = ProgressEvent()
    
    progress_thread = threading.Thread(target=print_progress_bar, args=(progress_event, total_tasks))
    progress_thread.start()
    
    with open("all_pairs.txt", 'w') as f:
        for i in range(len(list_stop)):
            for j in range(i + 1, len(list_stop)):
                stop_id1 = list_stop[i].getProperty("StopId")
                stop_id2 = list_stop[j].getProperty("StopId")
                
                initial = time.time()
                test1 = graph.aStarDistanceBase(stop_id1, stop_id2)
                final = time.time()
                
                if final - initial > max_time:
                    max_time = final - initial
                    max_time_pair = (stop_id1, stop_id2)
                if final - initial < min_time:
                    min_time = final - initial    
                    min_time_pair = (stop_id1, stop_id2)
                
                f.write(f"({stop_id1}, {stop_id2}) = {test1}\n")
                
                # Reverse way
                stop_id1 = list_stop[j].getProperty("StopId")
                stop_id2 = list_stop[i].getProperty("StopId")
                
                initial = time.time()
                test1 = graph.aStarDistanceBase(stop_id1, stop_id2)
                final = time.time()
                
                if final - initial > max_time:
                    max_time = final - initial
                    max_time_pair = (stop_id1, stop_id2)
                if final - initial < min_time:
                    min_time = final - initial    
                    min_time_pair = (stop_id1, stop_id2)
                
                f.write(f"({stop_id1}, {stop_id2}) = {test1}\n")
                
                progress_event.completed_tasks += 2
                
    end = time.time()
    
    progress_event.set()
    progress_thread.join()

    print(f"Total time cost: {end - start}")
    print(f"{min_time_pair} is fastest with the time cost is {min_time}")
    print(f"{max_time_pair} is slowest with the time cost is {max_time}")
