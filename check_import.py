import sys
import os
sys.path.append(os.getcwd())
try:
    from app.routers import products
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)
