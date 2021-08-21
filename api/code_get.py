import os
from pathlib import Path


async def get_code(module: str):
    try:
        return Path(module.replace('.', '/')+".py").read_text()
    except FileNotFoundError:
        return Path(module.replace('.', '/')+"/__init__.py").read_text()