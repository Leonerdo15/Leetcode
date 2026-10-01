"""
A diagnostic collector receives bundles from multiple customer tenants.

Each tenant is allowed up to **8 diagnostic units per service minute**, with service minutes measured from time `0`.

Implement:

```python
reserve(tenant_id, bundle_size, now)
```

`reserve(tenant_id, bundle_size, now)` should accept the entire bundle only if adding it would keep that tenant within
the **8-unit limit for the current minute**.

If the bundle would exceed the tenant’s remaining allowance, reject the entire bundle immediately.

Rules:

- Each tenant has its own independent allowance.
- The limit resets at the start of each new service minute.
- Unused allowance does not carry over to the next minute.
- A bundle must be accepted or rejected as a whole; partial acceptance is not allowed.

Explain any assumptions you make, then implement the component.
"""

class RateLimiter:
    def __init__(self):
        self.tenants = {}

    def reserve(self, tenant_id, bundle_size, now):
        current_minute = now // 60

        if tenant_id not in self.tenants:
            self.tenants[tenant_id] = {
                "minute": current_minute,
                "used": 0
            }

        tenant = self.tenants[tenant_id]

        # New minute -> reset the allowance
        if tenant["minute"] != current_minute:
            tenant["minute"] = current_minute
            tenant["used"] = 0

        # Reject the whole bundle if it would exceed the limit
        if tenant["used"] + bundle_size > 8:
            return False

        tenant["used"] += bundle_size
        return True

if __name__ == '__main__':
    collector = RateLimiter()

    # 1. Basic reservation
    assert collector.reserve("tenant-A", 3, 10) is True

    # 2. Same tenant can use remaining allowance
    assert collector.reserve("tenant-A", 5, 20) is True

    # 3. Cannot exceed 8 units in the same minute
    assert collector.reserve("tenant-A", 1, 30) is False

    # 4. Exact limit is allowed
    collector = RateLimiter()
    assert collector.reserve("tenant-B", 8, 15) is True

    # 5. Bundle larger than the full allowance is rejected
    collector = RateLimiter()
    assert collector.reserve("tenant-C", 9, 10) is False

    # 6. Rejected bundle does not consume allowance
    collector = RateLimiter()
    assert collector.reserve("tenant-D", 6, 10) is True
    assert collector.reserve("tenant-D", 4, 20) is False
    assert collector.reserve("tenant-D", 2, 30) is True

    # 7. Allowance resets in the next minute
    collector = RateLimiter()
    assert collector.reserve("tenant-E", 8, 59) is True
    assert collector.reserve("tenant-E", 8, 60) is True

    # 8. Different tenants have independent allowances
    collector = RateLimiter()
    assert collector.reserve("tenant-F", 8, 10) is True
    assert collector.reserve("tenant-G", 8, 10) is True

    # 9. One tenant being full does not affect another
    assert collector.reserve("tenant-F", 1, 20) is False
    assert collector.reserve("tenant-G", 1, 20) is False

    # 10. Unused allowance does not carry over
    collector = RateLimiter()
    assert collector.reserve("tenant-H", 3, 10) is True

    # New minute starts with 8 again, not 13
    assert collector.reserve("tenant-H", 8, 70) is True
    assert collector.reserve("tenant-H", 1, 75) is False

    print("All tests passed ✅")