def describe_changes(current, proposed, path=""):
    changes = []

    all_keys = set(current.keys()) | set(proposed.keys())

    for key in all_keys:
        current_path = f"{path}.{key}" if path else key

        # Added
        if key not in current:
            changes.append({
                "path": current_path,
                "type": "added",
                "new": proposed[key]
            })

        # Removed
        elif key not in proposed:
            changes.append({
                "path": current_path,
                "type": "removed",
                "old": current[key]
            })

        else:
            old_value = current[key]
            new_value = proposed[key]

            # Both are dictionaries -> compare recursively
            if isinstance(old_value, dict) and isinstance(new_value, dict):
                changes.extend(
                    describe_changes(
                        old_value,
                        new_value,
                        current_path
                    )
                )

            # Any other difference -> changed
            elif old_value != new_value:
                changes.append({
                    "path": current_path,
                    "type": "changed",
                    "old": old_value,
                    "new": new_value
                })

    return changes

if __name__ == '__main__':
    # 1. No changes
    current = {
        "workers": 4,
        "timeout": 30
    }

    proposed = {
        "workers": 4,
        "timeout": 30
    }

    assert describe_changes(current, proposed) == []

    # 2. Added setting
    current = {
        "workers": 4
    }

    proposed = {
        "workers": 4,
        "timeout": 30
    }

    result = describe_changes(current, proposed)

    assert {
               "path": "timeout",
               "type": "added",
               "new": 30
           } in result

    # 3. Removed setting
    current = {
        "workers": 4,
        "timeout": 30
    }

    proposed = {
        "workers": 4
    }

    result = describe_changes(current, proposed)

    assert {
               "path": "timeout",
               "type": "removed",
               "old": 30
           } in result

    # 4. Changed setting
    current = {
        "timeout": 30
    }

    proposed = {
        "timeout": 60
    }

    result = describe_changes(current, proposed)

    assert result == [
        {
            "path": "timeout",
            "type": "changed",
            "old": 30,
            "new": 60
        }
    ]

    # 5. Nested setting changed
    current = {
        "database": {
            "host": "db-old",
            "port": 5432
        }
    }

    proposed = {
        "database": {
            "host": "db-new",
            "port": 5432
        }
    }

    result = describe_changes(current, proposed)

    assert result == [
        {
            "path": "database.host",
            "type": "changed",
            "old": "db-old",
            "new": "db-new"
        }
    ]

    # 6. Deeply nested setting changed
    current = {
        "network": {
            "http": {
                "timeout": 30
            }
        }
    }

    proposed = {
        "network": {
            "http": {
                "timeout": 60
            }
        }
    }

    result = describe_changes(current, proposed)

    assert result == [
        {
            "path": "network.http.timeout",
            "type": "changed",
            "old": 30,
            "new": 60
        }
    ]

    # 7. Nested setting added
    current = {
        "database": {
            "host": "db"
        }
    }

    proposed = {
        "database": {
            "host": "db",
            "ssl": True
        }
    }

    result = describe_changes(current, proposed)

    assert {
               "path": "database.ssl",
               "type": "added",
               "new": True
           } in result

    # 8. Nested setting removed
    current = {
        "database": {
            "host": "db",
            "ssl": True
        }
    }

    proposed = {
        "database": {
            "host": "db"
        }
    }

    result = describe_changes(current, proposed)

    assert {
               "path": "database.ssl",
               "type": "removed",
               "old": True
           } in result

    # 9. Lists are compared as complete values
    current = {
        "servers": ["server-1", "server-2"]
    }

    proposed = {
        "servers": ["server-1", "server-3"]
    }

    result = describe_changes(current, proposed)

    assert result == [
        {
            "path": "servers",
            "type": "changed",
            "old": ["server-1", "server-2"],
            "new": ["server-1", "server-3"]
        }
    ]

    # 10. Dictionary replaced by another type
    current = {
        "logging": {
            "level": "info"
        }
    }

    proposed = {
        "logging": False
    }

    result = describe_changes(current, proposed)

    assert result == [
        {
            "path": "logging",
            "type": "changed",
            "old": {"level": "info"},
            "new": False
        }
    ]

    # 11. Non-dictionary replaced by dictionary
    current = {
        "cache": False
    }

    proposed = {
        "cache": {
            "enabled": True
        }
    }

    result = describe_changes(current, proposed)

    assert result == [
        {
            "path": "cache",
            "type": "changed",
            "old": False,
            "new": {"enabled": True}
        }
    ]

    # 12. Multiple different changes
    current = {
        "workers": 4,
        "timeout": 30,
        "database": {
            "host": "old-db",
            "port": 5432
        }
    }

    proposed = {
        "workers": 8,
        "database": {
            "host": "new-db",
            "port": 5432
        },
        "region": "eu"
    }

    result = describe_changes(current, proposed)

    assert {
               "path": "workers",
               "type": "changed",
               "old": 4,
               "new": 8
           } in result

    assert {
               "path": "timeout",
               "type": "removed",
               "old": 30
           } in result

    assert {
               "path": "database.host",
               "type": "changed",
               "old": "old-db",
               "new": "new-db"
           } in result

    assert {
               "path": "region",
               "type": "added",
               "new": "eu"
           } in result

    print("All tests passed ✅")