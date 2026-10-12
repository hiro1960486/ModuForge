"""Legacy command: delegate to the unified test suite."""
import sys,unittest
from pathlib import Path
root=Path(__file__).resolve().parent
suite=unittest.defaultTestLoader.discover(str(root/"tests"),pattern="test_tags.py",top_level_dir=str(root/"tests"))
sys.exit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
