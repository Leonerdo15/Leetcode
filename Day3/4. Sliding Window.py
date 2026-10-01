from collections import deque


class RotationGuard:
    def __init__(self):
        self.services = {}

    def rotate(self, service_id, now, rotation_operation):
        if service_id not in self.services:
            self.services[service_id] = deque()

        rotations = self.services[service_id]

        # Remove successful rotations that are 30+ seconds old
        while rotations and rotations[0] <= now - 30:
            rotations.popleft()

        # Already 2 successful rotations in the current window
        if len(rotations) >= 2:
            retry_at = rotations[0] + 30
            return False, retry_at

        # Run the operation.
        # If it raises an exception, we do NOT count it.
        result = rotation_operation()

        # Only successful completed operations count
        rotations.append(now)

        return True, result

if __name__ == '__main__':
    guard = RotationGuard()


    # 1. First rotation is allowed
    def rotation_1():
        return "rotated-1"


    assert guard.rotate("service-A", 0, rotation_1) == (
        True,
        "rotated-1"
    )


    # 2. Second rotation within 30 seconds is allowed
    def rotation_2():
        return "rotated-2"


    assert guard.rotate("service-A", 10, rotation_2) == (
        True,
        "rotated-2"
    )

    # 3. Third rotation within 30 seconds is blocked
    called = False


    def should_not_run():
        global called
        called = True
        return "should not happen"


    result = guard.rotate(
        "service-A",
        20,
        should_not_run
    )

    assert result == (False, 30)
    assert called is False


    # 4. At exactly 30 seconds, the rotation from time 0 expires
    def rotation_3():
        return "rotated-3"


    assert guard.rotate("service-A", 30, rotation_3) == (
        True,
        "rotated-3"
    )

    # 5. Different services have independent limits
    guard = RotationGuard()

    assert guard.rotate(
        "service-B",
        0,
        lambda: "B1"
    ) == (True, "B1")

    assert guard.rotate(
        "service-B",
        5,
        lambda: "B2"
    ) == (True, "B2")

    # B is now blocked
    assert guard.rotate(
        "service-B",
        10,
        lambda: "B3"
    ) == (False, 30)

    # C is completely independent
    assert guard.rotate(
        "service-C",
        10,
        lambda: "C1"
    ) == (True, "C1")

    # 6. Failed operation does NOT count
    guard = RotationGuard()


    def failing_rotation():
        raise RuntimeError("rotation failed")


    try:
        guard.rotate(
            "service-D",
            0,
            failing_rotation
        )
    except RuntimeError:
        pass

    # No successful rotation should have been stored
    assert len(guard.services["service-D"]) == 0

    # 7. After a failed operation, two successful rotations are still allowed
    assert guard.rotate(
        "service-D",
        1,
        lambda: "success-1"
    ) == (True, "success-1")

    assert guard.rotate(
        "service-D",
        2,
        lambda: "success-2"
    ) == (True, "success-2")

    # 8. Third successful rotation is blocked
    assert guard.rotate(
        "service-D",
        3,
        lambda: "success-3"
    ) == (False, 31)

    # 9. Retry time is based on the oldest successful rotation
    guard = RotationGuard()

    guard.rotate(
        "service-E",
        10,
        lambda: "E1"
    )

    guard.rotate(
        "service-E",
        25,
        lambda: "E2"
    )

    # Oldest rotation was at 10, so next attempt is at 40
    assert guard.rotate(
        "service-E",
        30,
        lambda: "E3"
    ) == (False, 40)

    # 10. Once the oldest rotation expires, another rotation is allowed
    assert guard.rotate(
        "service-E",
        40,
        lambda: "E3"
    ) == (True, "E3")

    # 11. Clock-minute boundaries do not matter
    guard = RotationGuard()

    assert guard.rotate(
        "service-F",
        50,
        lambda: "F1"
    ) == (True, "F1")

    assert guard.rotate(
        "service-F",
        59,
        lambda: "F2"
    ) == (True, "F2")

    # New clock minute, but still inside rolling 30-second window
    assert guard.rotate(
        "service-F",
        60,
        lambda: "F3"
    ) == (False, 80)

    print("All tests passed ✅")