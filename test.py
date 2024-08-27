from math import inf
import json
import time
import threading
import sys
from Graph import *
import random

graph = Graph()
graph.buildGraph("stops.json", "vars.json", "paths.json", "fixed_paths.json")
graph.draw_path(graph.aStarTimeBase(35, 72), "astar.html")
