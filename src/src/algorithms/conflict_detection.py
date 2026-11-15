import networkx as nx
from src.algorithms.temporal_checks import check_before
from src.services.graph_service import build_graph

def analyze(events, relationships):
    by_id = {int(e["event_id"]): e for e in events}
    graph = build_graph(events, relationships)
    conflicts = []
    for rel in relationships:
        a_id, b_id = int(rel["event_id_1"]), int(rel["event_id_2"])
        if a_id not in by_id or b_id not in by_id:
            continue
        if not check_before(by_id[a_id], by_id[b_id]):
            conflicts.append({
                "relationship_id": int(rel["relationship_id"]),
                "event_id_1": a_id, "event_id_2": b_id,
                "explanation": (
                    f"BEFORE rule violated: Event {a_id} ends at "
                    f"{by_id[a_id]['end_time']}, but Event {b_id} starts at "
                    f"{by_id[b_id]['start_time']}. The first event must finish "
                    "at or before the second event starts."
                )
            })
    if not nx.is_directed_acyclic_graph(graph):
        try:
            cycle = nx.find_cycle(graph)
            path = " → ".join(str(edge[0]) for edge in cycle) + f" → {cycle[0][0]}"
            conflicts.append({
                "relationship_id": None,
                "event_id_1": int(cycle[0][0]), "event_id_2": int(cycle[0][1]),
                "explanation": f"Ordering cycle detected ({path}). BEFORE relationships cannot contain a cycle."
            })
        except nx.NetworkXNoCycle:
            pass
    return conflicts
