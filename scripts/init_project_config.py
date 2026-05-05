from __future__ import annotations

import json
import sys
from pathlib import Path


def write_project_config(config_path: Path, project_root: Path) -> None:
    """Write the project-level config atomically."""

    payload = {"project_root": project_root.as_posix()}
    temp_path = config_path.with_name(f"{config_path.name}.tmp")

    with temp_path.open("w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, indent=2)
        file_handle.write("\n")

    temp_path.replace(config_path)


def main() -> int:
    """Create config.json in the project root."""

    project_root = Path.cwd().resolve()
    scripts_dir = project_root / "scripts"

    if not scripts_dir.is_dir():
        print(
            "Error: run this script from the project root. The current working directory must contain a scripts/ folder.",
            file=sys.stderr,
        )
        return 1

    config_path = project_root / "config.json"
    write_project_config(config_path, project_root)

    print(f"Created {config_path} with project_root={project_root.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())