import networkx as nx
from src.algorithms.temporal_checks import check_before
from src.services.graph_service import build_graph

def analyze(events, relationships):
    by_id={int(e["event_id"]):e for e in events}
    graph=build_graph(events,relationships)
    conflicts=[]
    for rel in relationships:
        a_id,b_id=int(rel["event_id_1"]),int(rel["event_id_2"])
        if not check_before(by_id[a_id],by_id[b_id]):
            conflicts.append({
              "relationship_id":int(rel["relationship_id"]),
              "event_id_1":a_id,"event_id_2":b_id,
              "explanation":f"BEFORE rule violated: Event {a_id} must finish before Event {b_id} starts."
            })
    if not nx.is_directed_acyclic_graph(graph):
        cycle=nx.find_cycle(graph)
        conflicts.append({
          "relationship_id":None,"event_id_1":int(cycle[0][0]),"event_id_2":int(cycle[0][1]),
          "explanation":"The event-order relationships contain a cycle."
        })
    return conflicts
