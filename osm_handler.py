import osmium as osm

class OSMGraph:
    def __init__(self, osm_file):
        self.osm_file = osm_file
        self.nodes = {}
        self.edges = {}

    class OSMHandler(osm.SimpleHandler):
        def __init__(self, osm_graph):
            osm.SimpleHandler.__init__(self)
            self.osm_graph = osm_graph
        
        def node(self, n):
            self.osm_graph.nodes[n.id] = (n.location.lat, n.location.lon)
        
        def way(self, w):
            nodes_in_way = w.nodes
            way_id = w.id
            for i in range(len(nodes_in_way) - 1):
                node1 = nodes_in_way[i].ref
                node2 = nodes_in_way[i + 1].ref
                self.osm_graph.edges[(node1, node2)] = way_id

    def parse_osm(self):
        handler = self.OSMHandler(self)
        handler.apply_file(self.osm_file)
    
    def build_graph(self):
        self.parse_osm()

    def get_graph(self):
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }

    def find_way_id(self, node1, node2):
        return self.edges.get((node1, node2), None) 
