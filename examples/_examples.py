"""
Some stuff needed for all the examples.
"""

# Add the parent directory to the PATH so the examples can be run without the
# ninja package needing to be installed.
import sys; sys.path.append('../')

try:
    import secrets
except ImportError as e:
    print e
    print """
        You need to add your access token and device GUIDs to a `secrets.py`
        file in this directory. See `secrets.py.example`.
    """
    sys.exit()