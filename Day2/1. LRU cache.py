"""
An edge worker repeatedly needs compiled versions of routing rules. Compiling a rule is expensive, so the worker should
reuse previously compiled results whenever possible. However, it can retain only a configured maximum number of compiled
rules.

Implement a function with an interface similar to:

`resolve(rule_id, compiler)`

where:

- `rule_id` identifies the routing rule that needs to be resolved.
- `compiler` is a function that compiles the rule and returns the compiled result.

If the requested rule is already retained, return the existing compiled result without calling `compiler` again.

If it is not retained, call `compiler`, store the returned result, and return it.

When storing a new result would exceed the configured capacity, discard the retained rule whose **most recent successful
use occurred longest ago**.

Explain the data structures and design choices you would use, then implement the component.
"""

class RuleResolver:
    def __init__(self, capacity):
        # Maximum number of compiled routing rules we are allowed to keep.
        self.capacity = capacity

        # Stores:
        # rule_id -> compiled result
        #
        # Example:
        # {
        #     "rule1": "compiled_rule1",
        #     "rule2": "compiled_rule2"
        # }
        #
        # The order also matters:
        # first item  = least recently used
        # last item   = most recently used
        self.cache = {}

    def resolve(self, rule_id, compiler):

        # Check if this rule has already been compiled and is still retained.
        if rule_id in self.cache:

            # Remove the existing compiled result from its current position.
            # We are not deleting it permanently.
            #
            # We do this because this rule has just been used again,
            # so it should no longer be considered "old".
            result = self.cache.pop(rule_id)

            # Add it back at the end.
            #
            # Python dictionaries preserve insertion order, so reinserting
            # the rule makes it the most recently used rule.
            self.cache[rule_id] = result

            # Return the already compiled result.
            #
            # compiler() is NOT called here because recompiling would be
            # unnecessary and expensive.
            return result

        # If we reach this point, the rule is not currently retained.
        # We therefore need to compile it.
        result = compiler(rule_id)

        self.cache[rule_id] = result

        # Check whether storing the new compiled result caused us to go
        # above the configured capacity.
        if len(self.cache) > self.capacity:

            # The first item in the dictionary is the least recently used,
            # because every rule that gets used is moved to the end.
            oldest = next(iter(self.cache))

            # Remove that least recently used compiled rule to make space.
            del self.cache[oldest]

        # Return the newly compiled result to the caller.
        return result


compile_calls = []


def compiler(rule_id):
    compile_calls.append(rule_id)
    return f"compiled_{rule_id}"

if __name__ == '__main__':

    # Test 1: first access should compile
    resolver = RuleResolver(2)

    assert resolver.resolve("rule1", compiler) == "compiled_rule1"
    assert compile_calls == ["rule1"]


    # Test 2: cached value should be reused
    assert resolver.resolve("rule1", compiler) == "compiled_rule1"
    assert compile_calls == ["rule1"]


    # Test 3: add another rule
    assert resolver.resolve("rule2", compiler) == "compiled_rule2"
    assert compile_calls == ["rule1", "rule2"]


    # Test 4: accessing rule1 makes it most recently used
    assert resolver.resolve("rule1", compiler) == "compiled_rule1"
    assert compile_calls == ["rule1", "rule2"]


    # Test 5: adding rule3 should evict rule2
    assert resolver.resolve("rule3", compiler) == "compiled_rule3"
    assert compile_calls == ["rule1", "rule2", "rule3"]

    assert "rule1" in resolver.cache
    assert "rule3" in resolver.cache
    assert "rule2" not in resolver.cache


    # Test 6: rule2 was evicted, so it must compile again
    assert resolver.resolve("rule2", compiler) == "compiled_rule2"
    assert compile_calls == ["rule1", "rule2", "rule3", "rule2"]


    print("All tests passed ✅")