from __future__ import annotations

import os
import sys

# Make the repository root importable when Render starts this file directly.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api.server import run


if __name__ == "__main__":
    run()
