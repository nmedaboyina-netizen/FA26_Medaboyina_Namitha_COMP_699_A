from src.algorithms.alternative_timelines import generate_alternatives

def test_topological_alternatives_obey_before():
    events=[{"event_id":1},{"event_id":2},{"event_id":3}]
    rels=[{"relationship_id":1,"event_id_1":1,"event_id_2":3}]
    orders=generate_alternatives(events,rels)
    assert orders
    assert all(order.index(1)<order.index(3) for order in orders)
