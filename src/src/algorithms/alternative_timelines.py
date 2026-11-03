import networkx as nx
from src.services.graph_service import build_graph

def generate_alternatives(events,relationships,limit=5):
    graph=build_graph(events,relationships)
    if not nx.is_directed_acyclic_graph(graph) or len(events)>9:
        return []
    results=[]
    for order in nx.all_topological_sorts(graph):
        results.append([int(x) for x in order])
        if len(results)>=limit:
            break
    return results
