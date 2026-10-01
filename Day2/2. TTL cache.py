"""
During an incident, a control service issues temporary handoff codes that route an operator to a destination.

Implement:

```python
issue(code, destination, lifetime, now)
redeem(code, now)
```

`issue(code, destination, lifetime, now)` assigns a code to a destination for a limited lifetime.

`redeem(code, now)` should return the destination only if the code:

- exists,
- has not expired, and
- has not already been redeemed.

A code can be successfully redeemed only once.

If the same code is issued again, the new assignment completely replaces the previous one, including its destination and
expiration time.

There is no background cleanup process. Expiration should be handled lazily when a code is accessed.

Explain any assumptions you make, then implement the component.
"""

class TTLCache:
    def __init__(self):
        self.codes = {}

    def issue(self, code, destination, lifetime, now):
        self.codes[code] = {
            "destination": destination,
            "expires_at": now + lifetime
        }

    def redeem(self, code, now):
        if code not in self.codes:
            return None

        entry = self.codes[code]

        if now >= entry["expires_at"]:
            del self.codes[code]
            return None

        destination = entry["destination"]

        # Remove it to not be possible to be redeemed again

        del self.codes[code]

        return destination

if __name__ == '__main__':
    service = TTLCache()

    # 1. Basic issue + redeem
    service.issue("ABC", "server-1", 10, 100)
    assert service.redeem("ABC", 105) == "server-1"

    # 2. Code can only be redeemed once
    assert service.redeem("ABC", 106) is None

    # 3. Expired code cannot be redeemed
    service.issue("DEF", "server-2", 10, 200)
    assert service.redeem("DEF", 210) is None

    # 4. Code just before expiration is still valid
    service.issue("GHI", "server-3", 10, 300)
    assert service.redeem("GHI", 309) == "server-3"

    # 5. Unknown code returns None
    assert service.redeem("UNKNOWN", 400) is None

    # 6. Reissuing a code replaces the old destination
    service.issue("JKL", "server-old", 10, 500)
    service.issue("JKL", "server-new", 20, 505)
    assert service.redeem("JKL", 510) == "server-new"

    # 7. Reissuing also replaces the old expiration time
    service.issue("MNO", "server-4", 5, 600)
    service.issue("MNO", "server-5", 20, 603)
    assert service.redeem("MNO", 615) == "server-5"

    # 8. Expired code gets removed lazily
    service.issue("PQR", "server-6", 5, 700)
    assert service.redeem("PQR", 706) is None
    assert "PQR" not in service.codes

    # 9. Successful redeem removes the code
    service.issue("STU", "server-7", 10, 800)
    assert service.redeem("STU", 805) == "server-7"
    assert "STU" not in service.codes

    # 10. Different codes work independently
    service.issue("AAA", "server-A", 10, 900)
    service.issue("BBB", "server-B", 20, 900)

    assert service.redeem("AAA", 905) == "server-A"
    assert service.redeem("BBB", 905) == "server-B"

    print("All tests passed ✅")