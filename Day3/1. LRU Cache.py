class FlowCollector:
    def __init__(self, capacity):
        self.capacity = capacity
        self.flows = {}

    def observe(self, flow_id, byte_count):
        evicted = None

        # Existing flow: update total and recency
        if flow_id in self.flows:
            total = self.flows.pop(flow_id)
            self.flows[flow_id] = total + byte_count
            return evicted

        # New flow and collector is full:
        # evict the least recently observed flow
        if len(self.flows) >= self.capacity:
            oldest_flow = next(iter(self.flows))
            oldest_total = self.flows.pop(oldest_flow)

            evicted = (oldest_flow, oldest_total)

        # New flow starts a fresh total
        self.flows[flow_id] = byte_count

        return evicted

    def summary(self, flow_id):
        # Reading must NOT update recency
        return self.flows.get(flow_id)

if __name__ == '__main__':
    collector = FlowCollector(3)

    # 1. First observation creates a flow
    assert collector.observe("flow-A", 100) is None
    assert collector.summary("flow-A") == 100

    # 2. More observations add to the existing total
    assert collector.observe("flow-A", 50) is None
    assert collector.summary("flow-A") == 150

    # 3. Multiple flows are tracked independently
    assert collector.observe("flow-B", 200) is None
    assert collector.observe("flow-C", 300) is None

    assert collector.summary("flow-A") == 150
    assert collector.summary("flow-B") == 200
    assert collector.summary("flow-C") == 300

    # Current recency:
    # flow-A, flow-B, flow-C
    # oldest ------------> newest

    # 4. Observing an existing flow updates its recency
    collector.observe("flow-A", 25)

    assert collector.summary("flow-A") == 175

    # New recency:
    # flow-B, flow-C, flow-A

    # 5. Adding a new flow when full evicts the least recently observed
    evicted = collector.observe("flow-D", 400)

    assert evicted == ("flow-B", 200)

    assert collector.summary("flow-B") is None
    assert collector.summary("flow-D") == 400

    # 6. summary() must NOT update recency
    collector = FlowCollector(3)

    collector.observe("flow-A", 100)
    collector.observe("flow-B", 200)
    collector.observe("flow-C", 300)

    # Reading A should NOT make it recent
    assert collector.summary("flow-A") == 100

    # A should still be the oldest and therefore be evicted
    evicted = collector.observe("flow-D", 400)

    assert evicted == ("flow-A", 100)

    # 7. An evicted flow starts fresh if it appears again
    assert collector.observe("flow-A", 50) == ("flow-B", 200)

    assert collector.summary("flow-A") == 50

    # 8. Unknown flow returns None
    assert collector.summary("does-not-exist") is None

    # 9. Reading an unknown flow does not create it
    assert collector.summary("flow-X") is None
    assert "flow-X" not in collector.flows

    # 10. Evicted summary contains the final accumulated total
    collector = FlowCollector(2)

    collector.observe("flow-A", 100)
    collector.observe("flow-A", 50)
    collector.observe("flow-B", 200)

    evicted = collector.observe("flow-C", 300)

    assert evicted == ("flow-A", 150)

    print("All tests passed ✅")