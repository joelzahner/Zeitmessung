# paths.py
import os, sys

def resource_path(name: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, name)

def data_dir() -> str:
    base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    d = os.path.join(base, "VCM_Zeitmessung", "Datenbank")
    os.makedirs(d, exist_ok=True)
    return d
