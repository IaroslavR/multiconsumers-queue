def pytest_assertrepr_compare(config, op, left, right):
    """Hook for PyCharm full diff
    References:
        https://stackoverflow.com/a/50625086/4249707"""
    if op in ("==", "!="):
        return ["{0} {1} {2}".format(left, op, right)]
