class ReplicaCopyLimiter:
    def __init__(self):
        self.replicas = {}

    def grant(self, replica_id, waiting_blocks, now_ms):
        # New replica starts with the full allowance
        if replica_id not in self.replicas:
            self.replicas[replica_id] = {
                "tokens": 9.0,
                "last_time": now_ms
            }

        replica = self.replicas[replica_id]

        # Time passed since this replica was last checked
        elapsed_ms = now_ms - replica["last_time"]

        # Recover 3 blocks per second
        recovered = (elapsed_ms / 1000) * 3

        replica["tokens"] = min(
            9.0,
            replica["tokens"] + recovered
        )

        replica["last_time"] = now_ms

        # Only whole blocks can be granted
        available_blocks = int(replica["tokens"])

        granted = min(
            waiting_blocks,
            available_blocks
        )

        # Consume the granted allowance
        replica["tokens"] -= granted

        return granted

if __name__ == '__main__':
    limiter = ReplicaCopyLimiter()

    # 1. New replica can immediately copy up to 9 blocks
    assert limiter.grant(
        "replica-A",
        9,
        0
    ) == 9

    # 2. No allowance remains immediately afterward
    assert limiter.grant(
        "replica-A",
        5,
        0
    ) == 0

    # 3. After 1 second, 3 blocks have recovered
    assert limiter.grant(
        "replica-A",
        5,
        1000
    ) == 3

    # 4. After another second, another 3 blocks recover
    assert limiter.grant(
        "replica-A",
        10,
        2000
    ) == 3

    # 5. Fractional recovery is kept internally
    limiter = ReplicaCopyLimiter()

    # Consume all 9 tokens
    assert limiter.grant(
        "replica-B",
        9,
        0
    ) == 9

    # 500 ms = 1.5 recovered tokens
    # Only 1 whole block may be granted
    assert limiter.grant(
        "replica-B",
        10,
        500
    ) == 1

    # 0.5 token remains internally
    # Another 500 ms adds 1.5 -> total 2.0
    assert limiter.grant(
        "replica-B",
        10,
        1000
    ) == 2

    # 6. Grant only what is actually waiting
    limiter = ReplicaCopyLimiter()

    assert limiter.grant(
        "replica-C",
        4,
        0
    ) == 4

    # Replica still has 5 tokens available
    assert limiter.grant(
        "replica-C",
        2,
        0
    ) == 2

    # 7. Allowance never grows above 9
    limiter = ReplicaCopyLimiter()

    # New replica already starts full
    assert limiter.grant(
        "replica-D",
        0,
        0
    ) == 0

    # Wait a long time
    assert limiter.grant(
        "replica-D",
        20,
        10000
    ) == 9

    # 8. Different replicas have independent allowances
    limiter = ReplicaCopyLimiter()

    assert limiter.grant(
        "replica-E",
        9,
        0
    ) == 9

    assert limiter.grant(
        "replica-F",
        9,
        0
    ) == 9

    assert limiter.grant(
        "replica-E",
        1,
        0
    ) == 0

    assert limiter.grant(
        "replica-F",
        1,
        0
    ) == 0

    # 9. Partial backlog is allowed
    limiter = ReplicaCopyLimiter()

    assert limiter.grant(
        "replica-G",
        20,
        0
    ) == 9

    # Remaining backlog can be requested later
    assert limiter.grant(
        "replica-G",
        11,
        1000
    ) == 3

    # 10. Empty backlog does not consume tokens
    limiter = ReplicaCopyLimiter()

    assert limiter.grant(
        "replica-H",
        9,
        0
    ) == 9

    # After 1 second, 3 tokens recover,
    # but there is nothing waiting
    assert limiter.grant(
        "replica-H",
        0,
        1000
    ) == 0

    # Those recovered tokens are still available
    assert limiter.grant(
        "replica-H",
        3,
        1000
    ) == 3

    # 11. 333 ms is not enough for one full block
    limiter = ReplicaCopyLimiter()

    assert limiter.grant(
        "replica-I",
        9,
        0
    ) == 9

    assert limiter.grant(
        "replica-I",
        1,
        333
    ) == 0

    # 12. Around 334 ms gives just over one token
    assert limiter.grant(
        "replica-I",
        1,
        334
    ) == 1

    print("All tests passed ✅")