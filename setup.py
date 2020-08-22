from pathlib import Path

import toml
from setuptools import setup

pyproject = Path(__file__).parent / "pyproject.toml"
config = toml.load(pyproject)["tool"]["briefcase"]


if __name__ == "__main__":
    name = config["name"]
    setup(name=name, install_requires=config["app"][name.replace("-", "_")]["requires"])
