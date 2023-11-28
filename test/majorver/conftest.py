def pytest_configure(config):
    marks = [
        "copyfiles((file, num),(file, num),...): which files to copy",
        "linkfiles((file, num),(file, num),...): which files to hardlink"
    ]

    def addmarkers(marks):
        for mark in marks:
            config.addinivalue_line("markers", mark)

    addmarkers(marks)