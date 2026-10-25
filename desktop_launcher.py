"""PyInstaller entry point for desktop package and packaging self-check."""
from __future__ import annotations

import json
from pathlib import Path
import sys


def package_self_check(path: Path) -> int:
    """Check packaged imports/assets without a display or physical DGX Spark.

    Explicitly NOT an end-to-end GUI, OS installer, or device acceptance test.
    """
    outcome = {"ok": False, "checks": {}, "scope": "packaging/import smoke only"}
    try:
        import uvicorn  # noqa: F401
        import webview  # noqa: F401
        from sparkcert.app import ASSETS, app
        from sparkcert import __version__

        for name in ("index.html", "styles.css", "app.js"):
            outcome["checks"][name] = (ASSETS / name).is_file()
        outcome["checks"]["fastapi_routes"] = any(
            getattr(r, "path", None) == "/api/health" for r in app.routes
        )
        outcome["version"] = __version__
        outcome["ok"] = all(outcome["checks"].values())
    except Exception as exc:
        outcome["error"] = f"{type(exc).__name__}: {exc}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(outcome, sort_keys=True, indent=2), encoding="utf-8")
    return 0 if outcome["ok"] else 1


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--package-self-check":
        raise SystemExit(package_self_check(Path(sys.argv[2])))
    from sparkcert.__main_desktop__ import main
    main()
