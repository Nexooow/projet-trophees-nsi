"""
Configuration pour pytest
Fais en sorte que lors de tests, il n'y ai pas de problème d'importations
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
