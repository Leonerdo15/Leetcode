from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self):
        self.sites = {}

    def dispatch(self, site_id, now):
        if site_id not in self.sites:
            self.sites[site_id] = deque()

        alerts = self.sites[site_id]

        # Remove alerts outside the 20-second window
        while alerts and alerts[0] <= now - 20:
            alerts.popleft()

        # Maximum 3 alerts in the last 20 seconds
        if len(alerts) >= 3:
            return False

        # Count alerts in the last 5 seconds
        alerts_last_5_seconds = 0

        for timestamp in reversed(alerts):
            if timestamp <= now - 5:
                break

            alerts_last_5_seconds += 1

        # Maximum 2 alerts in the last 5 seconds
        if alerts_last_5_seconds >= 2:
            return False

        alerts.append(now)
        return True


# =========================================================
# TEST 1 — Normal requests
# =========================================================

limiter = SlidingWindowRateLimiter()

assert limiter.dispatch("site1", 1) is True
assert limiter.dispatch("site1", 2) is True
assert limiter.dispatch("site1", 3) is False   # 2 already in last 5 sec

print("Test 1 passed")


# =========================================================
# TEST 2 — 5-second boundary
# =========================================================

limiter = SlidingWindowRateLimiter()

assert limiter.dispatch("site1", 0) is True
assert limiter.dispatch("site1", 1) is True

# At t=5, the alert at t=0 is exactly 5 seconds old,
# so it no longer counts toward the 5-second limit.
assert limiter.dispatch("site1", 5) is True

print("Test 2 passed")


# =========================================================
# TEST 3 — 20-second limit
# =========================================================

limiter = SlidingWindowRateLimiter()

assert limiter.dispatch("site1", 0) is True
assert limiter.dispatch("site1", 5) is True
assert limiter.dispatch("site1", 10) is True

# There are already 3 accepted alerts in the last 20 sec.
assert limiter.dispatch("site1", 15) is False

print("Test 3 passed")


# =========================================================
# TEST 4 — 20-second boundary
# =========================================================

limiter = SlidingWindowRateLimiter()

assert limiter.dispatch("site1", 0) is True
assert limiter.dispatch("site1", 5) is True
assert limiter.dispatch("site1", 10) is True

# At t=20, the alert at t=0 is exactly 20 seconds old
# and is removed.
assert limiter.dispatch("site1", 20) is True

print("Test 4 passed")


# =========================================================
# TEST 5 — Rejected alerts do NOT count
# =========================================================

limiter = SlidingWindowRateLimiter()

assert limiter.dispatch("site1", 0) is True
assert limiter.dispatch("site1", 1) is True

assert limiter.dispatch("site1", 2) is False
assert limiter.dispatch("site1", 3) is False
assert limiter.dispatch("site1", 4) is False

# Rejected alerts were never stored.
# At t=5, t=0 leaves the 5-second window.
assert limiter.dispatch("site1", 5) is True

print("Test 5 passed")


# =========================================================
# TEST 6 — Different sites have independent limits
# =========================================================

limiter = SlidingWindowRateLimiter()

assert limiter.dispatch("site1", 0) is True
assert limiter.dispatch("site1", 1) is True
assert limiter.dispatch("site1", 2) is False

# site2 has its own deque
assert limiter.dispatch("site2", 2) is True
assert limiter.dispatch("site2", 3) is True
assert limiter.dispatch("site2", 4) is False

print("Test 6 passed")


# =========================================================
# TEST 7 — 5-second limit can reject before 20-second limit
# =========================================================

limiter = SlidingWindowRateLimiter()

assert limiter.dispatch("site1", 10) is True
assert limiter.dispatch("site1", 11) is True

# Only 2 alerts exist in the 20-second window,
# so the 20-second rule is fine.
#
# But there are already 2 alerts in the last 5 seconds.
assert limiter.dispatch("site1", 12) is False

print("Test 7 passed")


# =========================================================
# TEST 8 — 20-second limit can reject even when 5-sec is fine
# =========================================================

limiter = SlidingWindowRateLimiter()

assert limiter.dispatch("site1", 0) is True
assert limiter.dispatch("site1", 6) is True
assert limiter.dispatch("site1", 12) is True

# No problem with the 5-second limit:
# only t=12 is within the last 5 seconds.
#
# But there are already 3 alerts in the last 20 seconds.
assert limiter.dispatch("site1", 18) is False

print("Test 8 passed")


print("\nALL TESTS PASSED ✅")