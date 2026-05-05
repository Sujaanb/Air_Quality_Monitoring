from __future__ import annotations

from common import load_project_root
from constants import SITE_ID
from make_fused_5min import build_fused_5min
from make_fused_hourly import build_fused_hourly


def main() -> None:
    """Run the full fusion pipeline for the configured site."""

    project_root = load_project_root()
    site_root = project_root / SITE_ID

    if not site_root.exists():
        raise FileNotFoundError(f"Site folder does not exist: {site_root}")

    build_fused_5min(project_root)
    build_fused_hourly(project_root)
    print(f"Fusion completed for: {site_root}")


if __name__ == "__main__":
    main()