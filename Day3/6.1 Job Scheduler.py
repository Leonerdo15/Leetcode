import heapq


class CertificateRolloutController:
    def __init__(self):
        self.waiting = []
        self.ready = []
        self.ticket_ids = set()
        self.order = 0

    def submit(self, ticket_id, earliest_release, urgency):
        if ticket_id in self.ticket_ids:
            raise ValueError("ticket_id already exists")

        self.ticket_ids.add(ticket_id)

        # Used to break ties by submission order
        order = self.order
        self.order += 1

        # waiting is ordered by:
        # earliest_release -> submission order
        heapq.heappush(
            self.waiting,
            (earliest_release, order, urgency, ticket_id)
        )

    def take_batch(self, now, available_slots):
        if available_slots <= 0:
            return []

        # Move all tickets that are now eligible
        # from waiting -> ready
        while self.waiting and self.waiting[0][0] <= now:
            earliest_release, order, urgency, ticket_id = heapq.heappop(
                self.waiting
            )

            # ready is ordered by:
            # urgency -> submission order
            heapq.heappush(
                self.ready,
                (urgency, order, ticket_id)
            )

        result = []

        # Take up to available_slots tickets
        while self.ready and len(result) < available_slots:
            urgency, order, ticket_id = heapq.heappop(self.ready)

            result.append(ticket_id)
            self.ticket_ids.remove(ticket_id)

        return result

if __name__ == '__main__':
    controller = CertificateRolloutController()

    # 1. Ticket cannot be released early
    controller.submit("ticket-A", 100, 1)

    assert controller.take_batch(99, 1) == []

    # 2. Ticket becomes available exactly at release time
    assert controller.take_batch(100, 1) == [
        "ticket-A"
    ]

    # 3. Returned ticket is removed
    assert controller.take_batch(200, 1) == []

    # 4. Lower urgency number is more urgent
    controller = CertificateRolloutController()

    controller.submit("ticket-A", 0, 5)
    controller.submit("ticket-B", 0, 1)
    controller.submit("ticket-C", 0, 3)

    assert controller.take_batch(0, 3) == [
        "ticket-B",
        "ticket-C",
        "ticket-A"
    ]

    # 5. available_slots limits the batch size
    controller = CertificateRolloutController()

    controller.submit("ticket-A", 0, 1)
    controller.submit("ticket-B", 0, 2)
    controller.submit("ticket-C", 0, 3)

    assert controller.take_batch(0, 2) == [
        "ticket-A",
        "ticket-B"
    ]

    # 6. Unselected ticket remains queued
    assert controller.take_batch(0, 2) == [
        "ticket-C"
    ]

    # 7. Future high-priority ticket must NOT be released early
    controller = CertificateRolloutController()

    controller.submit("available", 0, 5)
    controller.submit("future", 100, 1)

    assert controller.take_batch(50, 2) == [
        "available"
    ]

    assert controller.take_batch(99, 2) == []

    assert controller.take_batch(100, 2) == [
        "future"
    ]

    # 8. Same urgency -> earlier submitted ticket wins
    controller = CertificateRolloutController()

    controller.submit("first", 0, 2)
    controller.submit("second", 0, 2)
    controller.submit("third", 0, 2)

    assert controller.take_batch(0, 3) == [
        "first",
        "second",
        "third"
    ]

    # 9. Different release times do not override urgency
    # once both tickets are eligible
    controller = CertificateRolloutController()

    controller.submit("older-less-urgent", 0, 5)
    controller.submit("newer-more-urgent", 10, 1)

    assert controller.take_batch(10, 2) == [
        "newer-more-urgent",
        "older-less-urgent"
    ]

    # 10. Zero available slots returns nothing
    controller = CertificateRolloutController()

    controller.submit("ticket-A", 0, 1)

    assert controller.take_batch(0, 0) == []

    # Ticket should still be there
    assert controller.take_batch(0, 1) == [
        "ticket-A"
    ]

    # 11. Negative available slots also returns nothing
    controller = CertificateRolloutController()

    controller.submit("ticket-A", 0, 1)

    assert controller.take_batch(0, -5) == []

    assert controller.take_batch(0, 1) == [
        "ticket-A"
    ]

    # 12. Duplicate ticket IDs are rejected
    controller = CertificateRolloutController()

    controller.submit("ticket-A", 0, 1)

    try:
        controller.submit("ticket-A", 10, 2)
        assert False  # Should never reach here
    except ValueError:
        pass

    # 13. A used ticket ID can be submitted again later
    controller = CertificateRolloutController()

    controller.submit("ticket-A", 0, 1)

    assert controller.take_batch(0, 1) == [
        "ticket-A"
    ]

    controller.submit("ticket-A", 100, 2)

    assert controller.take_batch(100, 1) == [
        "ticket-A"
    ]

    # 14. Only eligible tickets enter the batch
    controller = CertificateRolloutController()

    controller.submit("ticket-A", 0, 3)
    controller.submit("ticket-B", 50, 1)
    controller.submit("ticket-C", 0, 2)
    controller.submit("ticket-D", 100, 0)

    assert controller.take_batch(25, 10) == [
        "ticket-C",
        "ticket-A"
    ]

    assert controller.take_batch(50, 10) == [
        "ticket-B"
    ]

    assert controller.take_batch(100, 10) == [
        "ticket-D"
    ]

    print("All tests passed ✅")