from .client import Chromeless, loads, dumps
try:
    from .__version__ import __version__
except Exception as e:
    from __version__ import __version__
