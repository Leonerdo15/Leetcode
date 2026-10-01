class OriginRetryTracker:
    def __init__(self):
        self.origins = {}

    def report_failure(self, origin_id, reason, retry_delay, now):
        retry_at = now + retry_delay

        # New origin: store the failure
        if origin_id not in self.origins:
            self.origins[origin_id] = {
                "reason": reason,
                "retry_at": retry_at
            }
            return

        current = self.origins[origin_id]

        # Only update if the new failure extends the wait
        if retry_at > current["retry_at"]:
            self.origins[origin_id] = {
                "reason": reason,
                "retry_at": retry_at
            }

    def check(self, origin_id, now):
        if origin_id not in self.origins:
            return False, None

        entry = self.origins[origin_id]

        # Exact retry time means the origin is allowed again
        if now >= entry["retry_at"]:
            del self.origins[origin_id]
            return False, None

        return True, entry["reason"]

if __name__ == '__main__':
    tracker = OriginRetryTracker()

    # 1. Unknown origin is not blocked
    assert tracker.check("origin-A", 100) == (False, None)

    # 2. Failure blocks the origin
    tracker.report_failure("origin-A", "timeout", 10, 100)

    assert tracker.check("origin-A", 105) == (True, "timeout")

    # 3. Origin is still blocked just before retry time
    assert tracker.check("origin-A", 109) == (True, "timeout")

    # 4. Exact retry-time boundary means it is allowed again
    assert tracker.check("origin-A", 110) == (False, None)

    # 5. Expired entry is removed lazily
    assert "origin-A" not in tracker.origins

    # 6. A shorter new retry must NOT bring the retry time forward
    tracker = OriginRetryTracker()

    tracker.report_failure("origin-B", "timeout", 20, 100)
    # retry_at = 120

    tracker.report_failure("origin-B", "connection reset", 5, 105)
    # new retry_at would be 110, so ignore it

    assert tracker.check("origin-B", 115) == (True, "timeout")
    assert tracker.check("origin-B", 120) == (False, None)

    # 7. A later retry time should extend the wait
    tracker = OriginRetryTracker()

    tracker.report_failure("origin-C", "timeout", 10, 100)
    # retry_at = 110

    tracker.report_failure("origin-C", "overloaded", 20, 105)
    # retry_at = 125

    assert tracker.check("origin-C", 115) == (True, "overloaded")
    assert tracker.check("origin-C", 124) == (True, "overloaded")
    assert tracker.check("origin-C", 125) == (False, None)

    # 8. check() must NOT prolong the wait
    tracker = OriginRetryTracker()

    tracker.report_failure("origin-D", "timeout", 10, 200)

    assert tracker.check("origin-D", 202) == (True, "timeout")
    assert tracker.check("origin-D", 205) == (True, "timeout")
    assert tracker.check("origin-D", 209) == (True, "timeout")

    # Still expires at the original time: 210
    assert tracker.check("origin-D", 210) == (False, None)

    # 9. Different origins are independent
    tracker = OriginRetryTracker()

    tracker.report_failure("origin-E", "timeout", 10, 300)
    tracker.report_failure("origin-F", "server error", 30, 300)

    assert tracker.check("origin-E", 305) == (True, "timeout")
    assert tracker.check("origin-F", 305) == (True, "server error")

    assert tracker.check("origin-E", 310) == (False, None)
    assert tracker.check("origin-F", 310) == (True, "server error")

    # 10. An expired origin can fail again and start a new wait
    tracker = OriginRetryTracker()

    tracker.report_failure("origin-G", "timeout", 5, 400)

    assert tracker.check("origin-G", 405) == (False, None)

    tracker.report_failure("origin-G", "connection refused", 10, 410)

    assert tracker.check("origin-G", 415) == (True, "connection refused")
    assert tracker.check("origin-G", 420) == (False, None)

    print("All tests passed ✅")