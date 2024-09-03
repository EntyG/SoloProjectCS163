from osm_handler import OSMGraph
from BusHistory import *

# Build edge matrix whose cell (i, j) is the most frequent edge between edge i and edge j
def most_frequent_edge_matrix(bus_history_file_path, osm_file_path):
    osm_graph = OSMGraph(osm_file_path)
    osm_graph.build_graph()

    bus_history_query = BusHistoryQuery()
    bus_history_query.readJSONInput(bus_history_file_path)
    bus_historys = bus_history_query.getBusHistorys()

    edge_matrix = {}
    for bus_history in bus_historys:
        trip_list = bus_history.getProperty('tripList')
        for trip in trip_list:
            edges = trip['edgesOfPath2']
            for i in range(len(edges) - 1):
                for j in range(i + 1, len(edges) - 1):
                    edge_1 = osm_graph.find_way_id(int(edges[i][0]), int(edges[i][1]))
                    edge_2 = osm_graph.find_way_id(int(edges[j][0]), int(edges[j][1]))
                    if not edge_1 or not edge_2 or edge_1 == edge_2:
                        continue
                    pre_way_id = None
                    for k in range(i + 1, j - 1):
                        node_1 = int(edges[k][0])
                        node_2 = int(edges[k][1])
                        way_id = osm_graph.find_way_id(node_1, node_2)
                        if way_id and way_id != pre_way_id:
                            if (edge_1, edge_2) not in edge_matrix:
                                edge_matrix[(edge_1, edge_2)] = {}
                            tmp = edge_matrix.get((edge_1, edge_2), {}).get(way_id, 0) + 1
                            edge_matrix[(edge_1, edge_2)][way_id] = tmp
                            pre_way_id = way_id

    ans = {}
    for key, _ in edge_matrix.items():
        for key2, value in edge_matrix[key].items():
            if value == max(edge_matrix[key].values()):
                ans[key] = key2
    return ans

def save_edge_matrix(edge_matrix, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        for key, value in edge_matrix.items():
            f.write(str(key) + ' = ' + str(value) + '\n')

import ast

def read_edge_matrix(file_name):
    edge_matrix = {}
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            key, value = line.split('=', 1)
            key = ast.literal_eval(key.strip())
            value = ast.literal_eval(value.strip())
            edge_matrix[key] = value
    return edge_matrix

def find_most_frequent_edge(edge_matrix, edge_i, edge_j):
    if (edge_i, edge_j) in edge_matrix:
        return edge_matrix[(edge_i, edge_j)]
    else:
        return None

