import networkx as nx

def build_graph(events, relationships):
    graph = nx.DiGraph()
    graph.add_nodes_from(int(e["event_id"]) for e in events)
    for rel in relationships:
        graph.add_edge(
            int(rel["event_id_1"]),
            int(rel["event_id_2"]),
            relationship_id=rel["relationship_id"]
        )
    return graph
