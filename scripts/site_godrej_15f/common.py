from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_jsonl(path: Path) -> pd.DataFrame:
    """Load a JSONL file into a DataFrame."""

    rows = []
    with path.open("r", encoding="utf-8") as file_handle:
        for line in file_handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def ensure_dirs(path: Path) -> None:
    """Create a directory tree if it does not exist."""

    path.mkdir(parents=True, exist_ok=True)


def to_timestamp(series: pd.Series) -> pd.Series:
    """Convert a timestamp-like series to UTC-aware datetimes."""

    return pd.to_datetime(series, utc=True)


def month_strings_from_dataframe(df: pd.DataFrame, ts_col: str) -> list[str]:
    """Return sorted YYYY-MM strings from a timestamp column."""

    months = sorted(df[ts_col].dt.strftime("%Y-%m").unique().tolist())
    return months


def find_config_path(start_path: Path | None = None) -> Path:
    """Find config.json by walking upward from the supplied path."""

    anchor = (start_path or Path(__file__)).resolve()
    directory = anchor if anchor.is_dir() else anchor.parent

    for candidate in [directory, *directory.parents]:
        config_path = candidate / "config.json"
        if config_path.is_file():
            return config_path

    raise FileNotFoundError(
        "Could not find config.json. Run python scripts/init_project_config.py from the project root first."
    )


def load_project_root() -> Path:
    """Load and validate the project root from config.json."""

    config_path = find_config_path()
    with config_path.open("r", encoding="utf-8") as file_handle:
        config = json.load(file_handle)

    project_root_value = config.get("project_root")
    if not isinstance(project_root_value, str) or not project_root_value.strip():
        raise ValueError(f"Invalid project_root in {config_path}.")

    project_root = Path(project_root_value).expanduser()
    if not project_root.is_absolute():
        raise ValueError(f"project_root in {config_path} must be an absolute path.")
    if not project_root.exists():
        raise FileNotFoundError(f"Configured project_root does not exist: {project_root}")

    return project_root


def resolve_project_relative_path(project_root: Path, relative_path: str | Path | None) -> Path | None:
    """Resolve a project-root-relative path to an absolute filesystem path."""

    if relative_path is None:
        return None

    relative_text = str(relative_path).strip()
    if not relative_text:
        return None

    return project_root / Path(relative_text)