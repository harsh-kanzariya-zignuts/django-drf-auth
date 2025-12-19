import os
from importlib import import_module

# Load settings based on DJANGO_ENV
env = os.getenv("DJANGO_ENV", "development")
module = import_module(f".{env}", "config.settings")
globals().update({k: v for k, v in module.__dict__.items() if not k.startswith("_")})
