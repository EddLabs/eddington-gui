from pathlib import Path

import matplotlib
import wx
import toml

matplotlib.use("WXAgg")
wx.DisableAsserts()

toml_file = toml.load(Path.cwd() / "pyproject.toml")
briefcase = toml_file["tool"]["briefcase"]
__version__ = briefcase["version"]
__author__ = briefcase["author"]
