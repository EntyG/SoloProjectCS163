from math import inf
import json
import time
import threading
import sys
from Graph import *
import random

graph = Graph()
graph.buildGraph("stops.json", "vars.json", "paths.json", "fixed_paths.json")
graph.draw_path(graph.aStarTimeBase(2419, 4424), "astar.html")
graph.draw_path(graph.dijkstraTimeBase(2419, 4424), "dijkstra.html")
graph.draw_path(graph.fastestPathWithCache(2419, 4424), "pathcatching.html")