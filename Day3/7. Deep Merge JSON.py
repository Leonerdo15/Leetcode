from copy import deepcopy


def build_profile(standard_profile, regional_override):
    # Start with an independent copy of the standard profile
    result = deepcopy(standard_profile)

    for key, regional_value in regional_override.items():

        # If both values are dictionaries, merge them recursively
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(regional_value, dict)
        ):
            result[key] = build_profile(
                result[key],
                regional_value
            )

        # Otherwise, the regional value replaces the standard one
        else:
            result[key] = deepcopy(regional_value)

    return result

if __name__ == '__main__':
    # 1. Standard-only settings remain
    standard = {
        "workers": 4,
        "timeout": 30
    }

    regional = {
        "timeout": 60
    }

    result = build_profile(standard, regional)

    assert result == {
        "workers": 4,
        "timeout": 60
    }

    # 2. Regional-only settings are added
    standard = {
        "workers": 4
    }

    regional = {
        "region": "eu-west"
    }

    result = build_profile(standard, regional)

    assert result == {
        "workers": 4,
        "region": "eu-west"
    }

    # 3. Regional value overrides a conflict
    standard = {
        "timeout": 30
    }

    regional = {
        "timeout": 90
    }

    result = build_profile(standard, regional)

    assert result["timeout"] == 90

    # 4. Nested dictionaries are merged
    standard = {
        "database": {
            "host": "default-db",
            "port": 5432,
            "ssl": True
        }
    }

    regional = {
        "database": {
            "host": "eu-db"
        }
    }

    result = build_profile(standard, regional)

    assert result == {
        "database": {
            "host": "eu-db",
            "port": 5432,
            "ssl": True
        }
    }

    # 5. Deeply nested dictionaries are merged recursively
    standard = {
        "network": {
            "http": {
                "timeout": 30,
                "retries": 3
            }
        }
    }

    regional = {
        "network": {
            "http": {
                "timeout": 60
            }
        }
    }

    result = build_profile(standard, regional)

    assert result == {
        "network": {
            "http": {
                "timeout": 60,
                "retries": 3
            }
        }
    }

    # 6. Lists are replaced, not merged
    standard = {
        "servers": ["server-1", "server-2"]
    }

    regional = {
        "servers": ["eu-server"]
    }

    result = build_profile(standard, regional)

    assert result["servers"] == ["eu-server"]

    # 7. Dictionary can be replaced by a non-dictionary
    standard = {
        "logging": {
            "level": "info"
        }
    }

    regional = {
        "logging": False
    }

    result = build_profile(standard, regional)

    assert result["logging"] is False

    # 8. Non-dictionary can be replaced by a dictionary
    standard = {
        "cache": False
    }

    regional = {
        "cache": {
            "enabled": True,
            "size": 100
        }
    }

    result = build_profile(standard, regional)

    assert result == {
        "cache": {
            "enabled": True,
            "size": 100
        }
    }

    # 9. Original standard profile must not be modified
    standard = {
        "database": {
            "host": "default-db"
        }
    }

    regional = {
        "database": {
            "host": "eu-db"
        }
    }

    result = build_profile(standard, regional)

    assert standard == {
        "database": {
            "host": "default-db"
        }
    }

    # 10. Original regional override must not be modified
    assert regional == {
        "database": {
            "host": "eu-db"
        }
    }

    # 11. Modifying the result must not modify the inputs
    standard = {
        "settings": {
            "timeout": 30
        }
    }

    regional = {
        "servers": ["eu-1", "eu-2"]
    }

    result = build_profile(standard, regional)

    result["settings"]["timeout"] = 999
    result["servers"].append("eu-3")

    assert standard["settings"]["timeout"] == 30
    assert regional["servers"] == ["eu-1", "eu-2"]

    # 12. Empty regional override returns equivalent standard config
    standard = {
        "workers": 4,
        "timeout": 30
    }

    result = build_profile(standard, {})

    assert result == standard
    assert result is not standard

    print("All tests passed ✅")