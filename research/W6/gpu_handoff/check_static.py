"""Dependency-free limited static lint: syntax, tabs, imports, unsafe execution APIs."""
import ast
import importlib.util
import json
from pathlib import Path
import tabnanny

root = Path(__file__).resolve().parent
errors = []
checked = []
for path in sorted((root/"w6kit").glob("*.py")) + sorted((root/"tests").glob("*.py")):
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))
    compile(tree, str(path), "exec")
    tabnanny.check(str(path))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                binding = alias.asname or (alias.name.split('.')[0] if isinstance(node, ast.Import) else alias.name)
                if binding not in names and binding != '*':
                    errors.append(f"{path.name}:{node.lineno}: unused import {binding}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"exec", "eval"}:
            errors.append(f"{path.name}:{node.lineno}: dynamic executable code prohibited")
    checked.append(str(path.relative_to(root)))
# pynvml is deliberately a lazy optional dependency; it is pinned, never vendored.
result = {"check": "limited_standard_library_static_lint", "files": checked, "errors": errors,
          "optional_nvml_binding_installed": importlib.util.find_spec("pynvml") is not None,
          "scope": "AST syntax, import-use and dynamic-execution lint; not a full type checker or third-party linter"}
print(json.dumps(result, indent=2))
raise SystemExit(1 if errors else 0)
