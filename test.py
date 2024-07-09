from math import inf
import time
import threading
import sys
from Graph import Graph
 
graph = Graph()
graph.buildGraph("stops.json", "vars.json", "paths.json")

stop1 = 7485
stop2 = 35

test = graph.aStarDistanceBase(stop2, stop1)

print(test)