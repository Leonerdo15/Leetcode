class DigestSelector:
    def __init__(self):
        self.sources = {}

    def select(self, source_id, records, now):
        current_minute = now // 60

        if source_id not in self.sources:
            self.sources[source_id] = {
                "minute": current_minute,
                "selected": 0
            }

        source = self.sources[source_id]

        # New minute -> reset the source's count
        if source["minute"] != current_minute:
            source["minute"] = current_minute
            source["selected"] = 0

        remaining = 4 - source["selected"]

        # Take only as many records as still fit
        chosen = records[:remaining]

        suppressed = len(records) - len(chosen)

        source["selected"] += len(chosen)

        return chosen, suppressed

if __name__ == '__main__':
    selector = DigestSelector()

    # 1. Page smaller than the limit
    chosen, suppressed = selector.select(
        "source-A",
        ["r1", "r2"],
        10
    )

    assert chosen == ["r1", "r2"]
    assert suppressed == 0

    # 2. Another page can use the remaining capacity
    chosen, suppressed = selector.select(
        "source-A",
        ["r3", "r4"],
        20
    )

    assert chosen == ["r3", "r4"]
    assert suppressed == 0

    # 3. Once 4 records have been selected, later records are suppressed
    chosen, suppressed = selector.select(
        "source-A",
        ["r5", "r6"],
        30
    )

    assert chosen == []
    assert suppressed == 2

    # 4. A page larger than the full allowance is partially accepted
    selector = DigestSelector()

    chosen, suppressed = selector.select(
        "source-B",
        ["a", "b", "c", "d", "e", "f"],
        10
    )

    assert chosen == ["a", "b", "c", "d"]
    assert suppressed == 2

    # 5. Partial page when only some capacity remains
    selector = DigestSelector()

    chosen, suppressed = selector.select(
        "source-C",
        ["a", "b", "c"],
        10
    )

    assert chosen == ["a", "b", "c"]
    assert suppressed == 0

    chosen, suppressed = selector.select(
        "source-C",
        ["d", "e", "f"],
        20
    )

    assert chosen == ["d"]
    assert suppressed == 2

    # 6. Records preserve their original order
    selector = DigestSelector()

    chosen, suppressed = selector.select(
        "source-D",
        ["first", "second", "third", "fourth", "fifth"],
        15
    )

    assert chosen == ["first", "second", "third", "fourth"]
    assert suppressed == 1

    # 7. Limit resets at the next minute
    selector = DigestSelector()

    chosen, suppressed = selector.select(
        "source-E",
        ["a", "b", "c", "d"],
        59
    )

    assert chosen == ["a", "b", "c", "d"]
    assert suppressed == 0

    chosen, suppressed = selector.select(
        "source-E",
        ["e", "f", "g", "h"],
        60
    )

    assert chosen == ["e", "f", "g", "h"]
    assert suppressed == 0

    # 8. Different sources have independent limits
    selector = DigestSelector()

    chosen, suppressed = selector.select(
        "source-F",
        [1, 2, 3, 4],
        10
    )

    assert chosen == [1, 2, 3, 4]
    assert suppressed == 0

    chosen, suppressed = selector.select(
        "source-G",
        [5, 6, 7, 8],
        10
    )

    assert chosen == [5, 6, 7, 8]
    assert suppressed == 0

    # 9. Empty page returns nothing and suppresses nothing
    selector = DigestSelector()

    chosen, suppressed = selector.select(
        "source-H",
        [],
        10
    )

    assert chosen == []
    assert suppressed == 0

    # 10. Suppressed records do not affect the next minute
    selector = DigestSelector()

    chosen, suppressed = selector.select(
        "source-I",
        ["a", "b", "c", "d", "e", "f"],
        50
    )

    assert chosen == ["a", "b", "c", "d"]
    assert suppressed == 2

    # New minute -> fresh limit of 4
    chosen, suppressed = selector.select(
        "source-I",
        ["g", "h", "i", "j"],
        60
    )

    assert chosen == ["g", "h", "i", "j"]
    assert suppressed == 0

    print("All tests passed ✅")