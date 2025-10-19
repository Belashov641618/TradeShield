import importlib.util
from pathlib import Path

def load_clauses(path:str):
    path = Path(path)
    clauses = []
    for py_file in path.glob("clause_*.py"):
        module_name = py_file.stem
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        clause_description = getattr(module, "__description__", None)
        clause_check = getattr(module, "check", None)
        clauses.append((clause_description, clause_check))
    return clauses
