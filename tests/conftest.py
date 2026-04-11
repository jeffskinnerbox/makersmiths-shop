"""tests/conftest.py

Shared setup and constants for the shop-sergeant test suite.
"""
import sys
from pathlib import Path

# Add scripts/ to sys.path once so every test file (and any script loaded via
# importlib) can import from it without each file repeating this line.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Shared constant used across QR-code tests.
MAKERSMITHS_URL = "https://makersmiths.org"
