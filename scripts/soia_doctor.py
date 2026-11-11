#!/usr/bin/env python3
"""Diagnostico de requisitos de SOIA Cine Studio. No instala ni modifica nada."""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys


def version(executable):
    try:
        # FFmpeg/FFprobe usan -version, no --version. Probamos ambas formas.
        for flag in ("--version", "-version"):
            result = subprocess.run(
                [executable, flag], capture_output=True, text=True,
                timeout=10, check=False,
            )
            output = (result.stdout or result.stderr).strip().splitlines()
            if result.returncode == 0 and output:
                return output[0]
        return None
    except (OSError, subprocess.TimeoutExpired):
        return None


def lookup(candidates):
    for name in candidates:
        found = shutil.which(name)
        if found:
            return found
    return None


def check(name, path, required_major=None):
    details = version(path) if path else None
    status = "ok" if details else "missing"
    if details and required_major is not None:
        found = re.search(r"\bv?(\d+)\.", details)
        if not found or int(found.group(1)) < required_major:
            status = "outdated"
    return {"name": name, "status": status, "path": path, "version": details}


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Mostrar JSON")
    parser.add_argument("--strict", action="store_true",
                        help="Salir con codigo 1 si falta un requisito")
    args = parser.parse_args()

    py_status = "ok" if sys.version_info >= (3, 9) else "outdated"
    checks = [{
        "name": "Python >= 3.9", "status": py_status,
        "path": sys.executable,
        "version": platform.python_version(),
    }]

    checks.append(check("Node.js >= 22", lookup(["node", "node.exe"]), 22))
    checks.append(check("FFmpeg", lookup(["ffmpeg", "ffmpeg.exe"])))
    checks.append(check("FFprobe", lookup(["ffprobe", "ffprobe.exe"])))

    chrome = os.environ.get("CHROME_PATH")
    if chrome and not os.path.isfile(chrome):
        chrome = None
    if not chrome:
        chrome = lookup([
            "google-chrome", "google-chrome-stable", "chromium",
            "chromium-browser", "microsoft-edge", "msedge",
        ])
    if not chrome and sys.platform == "darwin":
        candidate = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        chrome = candidate if os.path.isfile(candidate) else None
    checks.append(check("Chrome/Chromium", chrome))

    ready = all(item["status"] == "ok" for item in checks)
    report = {
        "project": "SOIA CINE STUDIO",
        "system": platform.platform(),
        "requirements_ready": ready,
        "gpu_verified": False,
        "mp4_render_verified": False,
        "checks": checks,
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("SOIA CINE STUDIO | Diagnostico de herramientas")
        for item in checks:
            print(f"- {item['name']}: {item['status']} | "
                  f"{item['version'] or 'no detectado'}")
        print("Requisitos:", "completos" if ready else "incompletos")
        print("GPU y MP4: aun NO verificados")
    return 0 if ready or not args.strict else 1


if __name__ == "__main__":
    sys.exit(run())
