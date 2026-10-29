#!/usr/bin/env python3
"""
Lint Runner - Unified linting and type checking
Runs appropriate linters based on project type.

Usage:
    python lint_runner.py <project_path>

Supports:
    - Node.js: npm run lint, npx tsc --noEmit
    - Python: ruff check, mypy
"""

import argparse
import subprocess
import sys
import json
import platform
import shutil
from pathlib import Path
from datetime import datetime

JS_SUFFIXES = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}

# Fix Windows console encoding
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except:
    pass


def detect_project_type(project_path: Path, files: list = None) -> dict:
    """Detect project type and available linters. With `files`, lint only those files
    (project-wide checks such as tsc, mypy and `npm run lint` are skipped)."""
    result = {
        "type": "unknown",
        "linters": []
    }
    
    # Node.js project
    package_json = project_path / "package.json"
    # Linters come from the project's own node_modules; `npx --no-install` never downloads packages
    # (this runs from the Stop hook, so it must not fetch code from the registry).
    deps_installed = (project_path / "node_modules").is_dir() or (project_path / ".pnp.cjs").exists()
    if package_json.exists() and not deps_installed:
        result["type"] = "node"
        result["skipped_reason"] = "JS linters skipped: dependencies not installed (no node_modules or .pnp.cjs); run the project's install first"
    elif package_json.exists():
        result["type"] = "node"
        try:
            pkg = json.loads(package_json.read_text(encoding='utf-8'))
            scripts = pkg.get("scripts", {})
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            
            if files is not None:
                js_files = [f for f in files if Path(f).suffix in JS_SUFFIXES]
                if js_files and "eslint" in deps:
                    result["linters"].append({"name": "eslint", "cmd": ["npx", "--no-install", "eslint", *js_files]})
            # Check for lint script
            elif "lint" in scripts:
                result["linters"].append({"name": "npm lint", "cmd": ["npm", "run", "lint"]})
            elif "eslint" in deps:
                result["linters"].append({"name": "eslint", "cmd": ["npx", "--no-install", "eslint", "."]})
            
            # Check for TypeScript
            if files is None and ("typescript" in deps or (project_path / "tsconfig.json").exists()):
                result["linters"].append({"name": "tsc", "cmd": ["npx", "--no-install", "tsc", "--noEmit"]})
                
        except:
            pass
    
    # Python project
    if (project_path / "pyproject.toml").exists() or (project_path / "requirements.txt").exists():
        result["type"] = "python"
        
        # Check for ruff
        if files is None:
            result["linters"].append({"name": "ruff", "cmd": ["ruff", "check", "."]})
        else:
            py_files = [f for f in files if f.endswith(".py")]
            if py_files:
                result["linters"].append({"name": "ruff", "cmd": ["ruff", "check", *py_files]})
        
        # Check for mypy
        if files is None and ((project_path / "mypy.ini").exists() or (project_path / "pyproject.toml").exists()):
            result["linters"].append({"name": "mypy", "cmd": ["mypy", "."]})
    
    return result


def run_linter(linter: dict, cwd: Path) -> dict:
    """Run a single linter and return results."""
    result = {
        "name": linter["name"],
        "passed": False,
        "output": "",
        "error": ""
    }
    
    try:
        cmd = linter["cmd"]
        
        # Windows compatibility for npm/npx
        if platform.system() == "Windows":
            if cmd[0] in ["npm", "npx"]:
                # Force .cmd extension on Windows
                if not cmd[0].lower().endswith(".cmd"):
                    cmd[0] = f"{cmd[0]}.cmd"
        
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=120,
            shell=platform.system() == "Windows" # Shell=True often helps with path resolution on Windows
        )
        
        result["output"] = proc.stdout[:2000] if proc.stdout else ""
        result["error"] = proc.stderr[:500] if proc.stderr else ""
        result["passed"] = proc.returncode == 0
        
    except FileNotFoundError:
        # A linter that isn't installed is skipped, not failed
        result["passed"] = True
        result["skipped"] = True
        result["error"] = f"Command not found: {linter['cmd'][0]} (skipped)"
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout after 120s"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Run the project's linters")
    parser.add_argument("project", nargs="?", default=".", help="Project path")
    parser.add_argument("--files", nargs="*", help="Lint only these files (paths relative to the project)")
    args = parser.parse_args()
    project_path = Path(args.project).resolve()
    
    print(f"\n{'='*60}")
    print(f"[LINT RUNNER] Unified Linting")
    print(f"{'='*60}")
    print(f"Project: {project_path}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detect project type
    project_info = detect_project_type(project_path, args.files)
    print(f"Type: {project_info['type']}")
    print(f"Linters: {len(project_info['linters'])}")
    print("-"*60)
    
    if not project_info["linters"]:
        print(project_info.get("skipped_reason") or "No linters found for this project type.")
        output = {
            "script": "lint_runner",
            "project": str(project_path),
            "type": project_info["type"],
            "checks": [],
            "passed": True,
            "message": project_info.get("skipped_reason") or "No linters configured"
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)
    
    # Run each linter
    results = []
    all_passed = True
    
    for linter in project_info["linters"]:
        print(f"\nRunning: {linter['name']}...")
        result = run_linter(linter, project_path)
        results.append(result)
        
        if result.get("skipped"):
            print(f"  [SKIP] {linter['name']}: {result['error']}")
        elif result["passed"]:
            print(f"  [PASS] {linter['name']}")
        else:
            print(f"  [FAIL] {linter['name']}")
            if result["error"]:
                print(f"  Error: {result['error'][:200]}")
            all_passed = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for r in results:
        icon = "[SKIP]" if r.get("skipped") else "[PASS]" if r["passed"] else "[FAIL]"
        print(f"{icon} {r['name']}")
    
    output = {
        "script": "lint_runner",
        "project": str(project_path),
        "type": project_info["type"],
        "checks": results,
        "passed": all_passed
    }
    
    print("\n" + json.dumps(output, indent=2))
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
