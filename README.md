# Air_Quality_Monitoring

This repository contains a small air-quality data pipeline and an example site dataset.

The repository uses one project root: the top-level `Air_Quality_Monitoring` folder. All stored `relative_path` values are relative to that root, not relative to an individual site folder.

## Path Convention

Example image path stored in manifests and fused files:

`site_godrej_15f/raw/images/2026-05-04/img_2026-05-04T06-00-00Z.jpg`

When code needs the actual file on disk, resolve it as:

`full_image_path = project_root / relative_path`

The project root is stored in `config.json` at the top level of the repository and is created by the bootstrap script.

## Layout

```text
Air_Quality_Monitoring/
  Design Decisions and Documentation/
    data_collection_stategy_decisions_v1.md
  config.json
  scripts/
    init_project_config.py
    site_godrej_15f/
      constants.py
      common.py
      make_fused_5min.py
      make_fused_hourly.py
      run_all.py
  site_godrej_15f/
    metadata/
      device_registry.json
      site_info.json
    raw/
      image_manifest.jsonl
      pm_sensor_raw.jsonl
      weather_sensor_raw.jsonl
      images/
        2026-05-04/
    logs/
    fused/
      fused_5min/
        2026-05.csv
        2026-05.parquet
      fused_hourly/
        2026-05.csv
        2026-05.parquet
  README.md
  requirements.txt
```

## Workflow

1. Open a terminal in the `Air_Quality_Monitoring` project root.
2. Run `python scripts/init_project_config.py`.
3. Run `python scripts/site_godrej_15f/run_all.py`.
4. Monthly fused CSV and Parquet files are created under:
   - `site_godrej_15f/fused/fused_5min/`
   - `site_godrej_15f/fused/fused_hourly/`

## Scripts

The site-specific scripts live under `scripts/site_godrej_15f/` and load the project root from `config.json` automatically.

- `constants.py` contains stable site settings such as `SITE_ID`.
- `common.py` contains shared file-loading and config-resolution helpers.
- `make_fused_5min.py` generates the monthly 5-minute fused outputs.
- `make_fused_hourly.py` generates the monthly hourly fused outputs.
- `run_all.py` runs both fusion steps in sequence.

The individual fusion scripts can also be run directly from the project root:

```bash
python scripts/site_godrej_15f/make_fused_5min.py
python scripts/site_godrej_15f/make_fused_hourly.py
```

## Config Bootstrap

`scripts/init_project_config.py` must be run from the `Air_Quality_Monitoring` project root. It validates that the current working directory contains `scripts/` and then writes `config.json` with the absolute project root.

That file is the single source of truth for the rest of the pipeline. If the top-level folder is renamed, run the bootstrap script again so `config.json` is refreshed with the new absolute path.

## Data Assumptions

- PM sensor data is sampled every 10 seconds.
- Weather sensor data is sampled every 5 minutes.
- Images are captured every 5 minutes during daytime only.
- The data collection device stores raw data and logs only.
- Fused files are generated on a separate analysis machine.
- Night-time fused rows may have no image metadata, so `image_id`, `relative_path`, and `image_available` can be empty or false.

## Outputs

The fusion scripts regenerate the monthly partitioned outputs:

- `site_godrej_15f/fused/fused_5min/YYYY-MM.csv`
- `site_godrej_15f/fused/fused_5min/YYYY-MM.parquet`
- `site_godrej_15f/fused/fused_hourly/YYYY-MM.csv`
- `site_godrej_15f/fused/fused_hourly/YYYY-MM.parquet`

## Install

```bash
pip install -r requirements.txt
```

## Notes

- Relative paths in manifests and fused outputs are always project-root-relative.
- The scripts are Windows-friendly and use `pathlib` for path handling.
