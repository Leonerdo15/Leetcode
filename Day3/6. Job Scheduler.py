class MaintenanceScheduler:
    def __init__(self):
        self.commands = []
        self.next_ticket = 1

    def queue(self, label, earliest_start, expires_at, severity):
        ticket = self.next_ticket
        self.next_ticket += 1

        self.commands.append({
            "ticket": ticket,
            "label": label,
            "earliest_start": earliest_start,
            "expires_at": expires_at,
            "severity": severity
        })

        return ticket

    def choose(self, now):
        valid_commands = []

        # Remove expired commands
        for command in self.commands:
            if now < command["expires_at"]:
                valid_commands.append(command)

        self.commands = valid_commands

        best = None

        # Find the most severe command whose window is open
        for command in self.commands:
            if command["earliest_start"] <= now:

                if best is None:
                    best = command

                elif command["severity"] > best["severity"]:
                    best = command

                # Same severity -> older ticket wins
                elif (
                    command["severity"] == best["severity"]
                    and command["ticket"] < best["ticket"]
                ):
                    best = command

        if best is None:
            return None

        self.commands.remove(best)

        return best

if __name__ == '__main__':
    scheduler = MaintenanceScheduler()

    # 1. queue() returns unique ticket numbers
    ticket1 = scheduler.queue(
        "restart-db",
        10,
        30,
        5
    )

    ticket2 = scheduler.queue(
        "restart-cache",
        10,
        30,
        3
    )

    assert ticket1 == 1
    assert ticket2 == 2

    # 2. Command cannot run before earliest_start
    assert scheduler.choose(5) is None

    # 3. now == earliest_start is allowed
    result = scheduler.choose(10)

    assert result["ticket"] == 1
    assert result["label"] == "restart-db"
    assert result["severity"] == 5

    # 4. Chosen command is removed
    result = scheduler.choose(10)

    assert result["ticket"] == 2
    assert result["label"] == "restart-cache"

    # 5. Nothing remains
    assert scheduler.choose(10) is None

    # 6. Highest severity wins
    scheduler = MaintenanceScheduler()

    scheduler.queue(
        "command-A",
        0,
        100,
        2
    )

    scheduler.queue(
        "command-B",
        0,
        100,
        10
    )

    scheduler.queue(
        "command-C",
        0,
        100,
        5
    )

    result = scheduler.choose(20)

    assert result["label"] == "command-B"
    assert result["severity"] == 10

    # 7. Future command must not be selected,
    # even if it has higher severity
    scheduler = MaintenanceScheduler()

    scheduler.queue(
        "available",
        0,
        100,
        5
    )

    scheduler.queue(
        "future",
        50,
        100,
        100
    )

    result = scheduler.choose(20)

    assert result["label"] == "available"

    # 8. Future command remains queued
    result = scheduler.choose(50)

    assert result["label"] == "future"

    # 9. now == expires_at means the command is expired
    scheduler = MaintenanceScheduler()

    scheduler.queue(
        "expired",
        10,
        30,
        100
    )

    assert scheduler.choose(30) is None

    # 10. Just before expires_at, the command is still valid
    scheduler = MaintenanceScheduler()

    scheduler.queue(
        "still-valid",
        10,
        30,
        5
    )

    result = scheduler.choose(29)

    assert result["label"] == "still-valid"

    # 11. Expired commands are discarded
    scheduler = MaintenanceScheduler()

    scheduler.queue(
        "old-command",
        0,
        10,
        100
    )

    scheduler.queue(
        "valid-command",
        0,
        50,
        2
    )

    result = scheduler.choose(20)

    assert result["label"] == "valid-command"

    # Expired command should have been removed
    assert len(scheduler.commands) == 0

    # 12. Same severity -> lower ticket / older command wins
    scheduler = MaintenanceScheduler()

    ticket1 = scheduler.queue(
        "first",
        0,
        100,
        5
    )

    ticket2 = scheduler.queue(
        "second",
        0,
        100,
        5
    )

    result = scheduler.choose(10)

    assert result["ticket"] == ticket1
    assert result["label"] == "first"

    # 13. The second command is still available afterward
    result = scheduler.choose(10)

    assert result["ticket"] == ticket2
    assert result["label"] == "second"

    # 14. A command whose window has not opened remains queued
    scheduler = MaintenanceScheduler()

    scheduler.queue(
        "later",
        100,
        200,
        10
    )

    assert scheduler.choose(50) is None
    assert len(scheduler.commands) == 1

    result = scheduler.choose(100)

    assert result["label"] == "later"

    # 15. Expired high-severity command must not beat valid lower-severity one
    scheduler = MaintenanceScheduler()

    scheduler.queue(
        "expired-high",
        0,
        20,
        100
    )

    scheduler.queue(
        "valid-low",
        0,
        100,
        1
    )

    result = scheduler.choose(30)

    assert result["label"] == "valid-low"

    print("All tests passed ✅")