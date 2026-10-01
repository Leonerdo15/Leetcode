"""
An incident service sends alerts for multiple customer sites.

Each site may have at most **3 accepted alerts within the previous 20 seconds**.

Unlike a fixed-window limiter, this limit is based on a **rolling 20-second window** and does not reset when a clock
minute changes.

Implement:

```python
dispatch(site_id, now)
```

`dispatch(site_id, now)` should return whether a new alert may be sent immediately.

Rules:

- Each site has its own independent limit.
- At most **3 accepted alerts** may exist inside the current 20-second window.
- Only accepted alerts count toward the limit.
- Denied alerts are dropped immediately and should not be stored.
- Old alerts that fall outside the 20-second window should no longer count.
- There is no need for background cleanup; remove expired timestamps when that site is accessed.

Clearly explain how you handle the exact 20-second boundary, choose an appropriate data structure, and implement the component.
"""

from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self):
        # Each site_id maps to a deque of timestamps of accepted alerts
        self.sites = {}

    def dispatch(self, site_id, now):
        if site_id not in self.sites:
            self.sites[site_id] = deque()

        alerts = self.sites[site_id]

        # Remove alerts that are outside the 20-second window
        while alerts and alerts[0] <= now - 20:
            alerts.popleft()

        # Already 3 accepted alerts in the current window
        if len(alerts) >= 3:
            return False

        # Accept this alert and store its timestamp
        alerts.append(now)

        return True

if __name__ == '__main__':
    dispatcher = SlidingWindowRateLimiter()

    assert dispatcher.dispatch("site-B", 20) is True
    assert dispatcher.dispatch("site-B", 20) is True
    assert dispatcher.dispatch("site-B", 20) is True
    assert dispatcher.dispatch("site-B", 40) is True

    print("All tests passed ✅")