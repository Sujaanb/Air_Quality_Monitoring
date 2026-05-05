from __future__ import annotations

from pathlib import Path

import pandas as pd

from common import ensure_dirs, load_jsonl, load_project_root, month_strings_from_dataframe, to_timestamp
from constants import SITE_ID


def build_fused_5min(project_root: Path) -> None:
    """Build monthly 5-minute fused outputs for the configured site."""

    site_root = project_root / SITE_ID
    raw = site_root / "raw"
    fused_dir = site_root / "fused" / "fused_5min"
    ensure_dirs(fused_dir)

    pm = load_jsonl(raw / "pm_sensor_raw.jsonl")
    wx = load_jsonl(raw / "weather_sensor_raw.jsonl")
    img = load_jsonl(raw / "image_manifest.jsonl")

    pm["timestamp_utc"] = to_timestamp(pm["timestamp_utc"])
    wx["timestamp_utc"] = to_timestamp(wx["timestamp_utc"])
    img["timestamp_utc"] = to_timestamp(img["timestamp_utc"])

    months = month_strings_from_dataframe(pm, "timestamp_utc")

    for month in months:
        pm_m = pm[pm["timestamp_utc"].dt.strftime("%Y-%m") == month].copy()
        wx_m = wx[wx["timestamp_utc"].dt.strftime("%Y-%m") == month].copy()
        img_m = img[img["timestamp_utc"].dt.strftime("%Y-%m") == month].copy()

        pm_m["window_start_utc"] = pm_m["timestamp_utc"].dt.floor("5min")
        pm_agg = (
            pm_m.groupby("window_start_utc", as_index=False)
            .agg(
                pm25_mean_ug_m3=("pm25_ug_m3", "mean"),
                pm10_mean_ug_m3=("pm10_ug_m3", "mean"),
                pm_sensor_count=("event_id", "count"),
            )
        )
        pm_agg["window_end_utc"] = pm_agg["window_start_utc"] + pd.Timedelta(minutes=5)
        pm_agg["anchor_timestamp_utc"] = pm_agg["window_end_utc"]

        wx_m["window_start_utc"] = wx_m["timestamp_utc"].dt.floor("5min")
        wx_agg = wx_m[["window_start_utc", "temperature_c", "humidity_pct", "pressure_hpa"]].drop_duplicates(
            "window_start_utc"
        )

        img_m["window_start_utc"] = img_m["timestamp_utc"].dt.floor("5min")
        img_agg = (
            img_m.sort_values("timestamp_utc")[["window_start_utc", "image_id", "relative_path"]]
            .drop_duplicates("window_start_utc", keep="first")
        )
        img_agg["image_available"] = True

        fused = pm_agg.merge(wx_agg, on="window_start_utc", how="left")
        fused = fused.merge(img_agg, on="window_start_utc", how="left")
        fused["image_available"] = fused["image_available"].astype("boolean").fillna(False)
        fused["site_id"] = SITE_ID
        fused["record_id"] = [f"f5_{month}_{i + 1:06d}" for i in range(len(fused))]

        cols = [
            "record_id",
            "site_id",
            "window_start_utc",
            "window_end_utc",
            "anchor_timestamp_utc",
            "image_id",
            "relative_path",
            "pm25_mean_ug_m3",
            "pm10_mean_ug_m3",
            "temperature_c",
            "humidity_pct",
            "pressure_hpa",
            "pm_sensor_count",
            "image_available",
        ]
        fused = fused[cols].sort_values("window_start_utc").reset_index(drop=True)
        fused["pm25_mean_ug_m3"] = fused["pm25_mean_ug_m3"].round(3)
        fused["pm10_mean_ug_m3"] = fused["pm10_mean_ug_m3"].round(3)

        fused.to_csv(fused_dir / f"{month}.csv", index=False)
        fused.to_parquet(fused_dir / f"{month}.parquet", index=False)


def main() -> None:
    """Run the 5-minute fusion pipeline for the configured project."""

    project_root = load_project_root()
    build_fused_5min(project_root)


if __name__ == "__main__":
    main()