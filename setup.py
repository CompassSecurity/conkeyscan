from setuptools import setup, find_packages

setup(
    name="conkeyscan",
    author="Jan Friedli",
    description="A Pentesters Confluence Keyword Scanner",
    version="{{VERSION_PLACEHOLDER}}",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
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
    entry_points={
        "console_scripts": ["conkeyscan = conkeyscan.conkeyscan:entry_point"]
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={"conkeyscan.config": ["*.txt"]},
)
