from math import inf
import json
import time
import threading
import sys
from Graph import Graph
import random

graph = Graph()
graph.buildGraph("stops.json", "vars.json", "paths.json", "fixed_paths.json")
graph.pathCatchingPrecompute()
