"""Pytest configuration for gateway reader unit tests."""

import sys
from pathlib import Path


COMPONENT_DIR = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "enphase_gateway"
)

# Import gateway_reader directly so unit tests do not require the full
# Home Assistant package just to execute the standalone reader code.
sys.path.insert(0, str(COMPONENT_DIR))
