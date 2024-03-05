from setuptools import setup

setup(
    name="conkeyscan",
    version="0.1.0",
    py_modules=["conkeyscan"],
    install_requires=[
        "loguru",
        "atlassian-python-api>=3",
        "beautifulsoup4>=4",
        "requests-ratelimiter",
        "clize>=5",
        "random-user-agent>=1",
        "readchar",
        "PySocks>=1",
    ],
    entry_points={"console_scripts": ["conkeyscan = conkeyscan:entry_point"]},
)
