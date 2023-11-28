def pytest_configure(config):
    config.addinivalue_line(
        "markers", "copyfiles((file, num),(file, num),...): which files to copy"
    )
    config.addinivalue_line(
        "markers", "linkfiles((file, num),(file, num),...): which files to hardlink"
    )