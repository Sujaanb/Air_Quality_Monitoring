# Data Collection and Storage Workflow (Version 1)

I would like to share the current Version 1 of my data collection and storage workflow for the preliminary pilot study. This note summarizes:

1. the data collection structure on the Raspberry Pi and on my laptop,
2. the schema of the data files,
3. the file formats selected and the reason for selecting them,
4. and the end-to-end workflow from data acquisition to fusion and analysis.

My intention is to keep the system simple, modular, and scalable, while ensuring that the raw multimodal data remain clean and portable for later processing.

---

## 1. Current Design Principles

The current design is based on the following principles:

- each **site is fully separated** from other sites at the folder level,
- the **Raspberry Pi stores only raw data and logs**,
- the **laptop stores the backed-up raw data and the fused datasets**,
- raw data are stored **modality-wise**,
- fused datasets are generated **after backup** on the laptop,
- the structure should remain valid even if more sites are added later.

This design is intended to support both practical implementation and later scalability.

---

## 2. Current Collection Schedule

The current collection intervals are:

- **PM sensor:** every **10 seconds**
- **weather sensor:** every **5 minutes**
- **camera:** every **5 minutes during daytime only**

The reason for this design is:

- PM data are expected to vary more quickly, so denser sampling is useful,
- local weather data change more slowly, so a 5-minute interval is sufficient,
- image capture every 5 minutes provides good temporal coverage while keeping storage manageable,
- daytime-only image capture avoids collecting low-value nighttime images while still allowing the sensors to run continuously.

---

## 3. Raspberry Pi Storage Structure

The Raspberry Pi is used only for **metadata storage, raw data collection, image storage, and operational logs**.  
It does **not** store fused datasets.

### Pi-side folder structure

```text
~/aqpilot/
  site_godrej_15f/
    metadata/
      site_info.json
      device_registry.json
    raw/
      pm_sensor_raw.jsonl
      weather_sensor_raw.jsonl
      image_manifest.jsonl
      images/
        2026-05-04/
        2026-05-05/
        ...
    logs/
      pm_capture.log
      weather_capture.log
      image_capture.log
````

### Why this structure was chosen

* it keeps each site fully independent,
* raw sensor/image data remain separate and easy to inspect,
* the Pi is used only as a collection node,
* the processing logic remains on the laptop, which makes iteration easier.

---

## 4. Laptop Storage Structure

After backup, the laptop stores:

* a copy of the Pi-side data,
* and the fused datasets generated from the raw data.

### Laptop-side folder structure

```text
~/aqpilot_backup/
  scripts/
  site_godrej_15f/
    metadata/
      site_info.json
      device_registry.json
    raw/
      pm_sensor_raw.jsonl
      weather_sensor_raw.jsonl
      image_manifest.jsonl
      images/
        2026-05-04/
        2026-05-05/
        ...
    logs/
      pm_capture.log
      weather_capture.log
      image_capture.log
    fused/
      fused_5min/
        2026-05.parquet
        2026-05.csv
        ...
      fused_hourly/
        2026-05.parquet
        2026-05.csv
        ...
```

### Why this structure was chosen

* the backed-up raw data remain identical in structure to the Pi-side data,
* fused datasets are separated from raw data,
* fused files are easier to regenerate, manage, and inspect than one continuously growing master file.

---

## 5. File Types and Why They Were Chosen

### 5.1 `json`

Used for:

* `site_info.json`
* `device_registry.json`

**Reason:**
These are small structured metadata files that are read occasionally and may be manually edited if needed. JSON is simple, readable, and well suited for configuration-style data.

### 5.2 `jsonl`

Used for:

* `pm_sensor_raw.jsonl`
* `weather_sensor_raw.jsonl`
* `image_manifest.jsonl`

**Reason:**
These files are append-oriented. Each new reading or event can be written as one new JSON object on one new line. This makes the format suitable for continuous logging from the Raspberry Pi.

### 5.3 `csv`

Used for:

* human-readable fused datasets

**Reason:**
CSV is easy to inspect manually, open in spreadsheet tools, and share for quick review.

### 5.4 `parquet`

Used for:

* analysis-oriented fused datasets

**Reason:**
Parquet is compact and efficient for structured tabular data and is well suited for later analytics and modeling. It is less human-readable than CSV, but better for computation.

### 5.5 plain text log files (`.log`)

Used for:

* `pm_capture.log`
* `weather_capture.log`
* `image_capture.log`

**Reason:**
These files are not scientific data files. They are operational records to help diagnose issues such as script failures, sensor read errors, skipped image captures, or restarts.

---

## 6. Metadata File Schemas

## 6.1 `metadata/site_info.json`

This file stores site-level information that is stable over time.

### Schema

| Field                     | Description                                       | Reason                                                |
| ------------------------- | ------------------------------------------------- | ----------------------------------------------------- |
| `site_id`                 | machine-readable site identifier                  | needed for portability and future merging             |
| `site_name`               | human-readable site name                          | useful for documentation                              |
| `location_name`           | full location text                                | useful for reporting and later interpretation         |
| `latitude`                | latitude of the site                              | useful for spatial reference                          |
| `longitude`               | longitude of the site                             | useful for spatial reference                          |
| `floor_level`             | floor of deployment                               | important because the first site is on the 15th floor |
| `deployment_environment`  | deployment type such as `windowside_semi_outdoor` | helps interpret the measurements                      |
| `camera_view_description` | short description of the camera framing           | useful for later data interpretation                  |
| `installation_date`       | date of site installation                         | useful for tracking deployment timeline               |
| `notes`                   | additional remarks                                | flexible field for site-specific comments             |

---

## 6.2 `metadata/device_registry.json`

This file stores the list of devices installed at the site.
There is **one device registry file per site**, with **one entry per device**.

### Schema

| Field                     | Description                                          | Reason                                           |
| ------------------------- | ---------------------------------------------------- | ------------------------------------------------ |
| `device_id`               | unique identifier of the device                      | useful if devices are replaced or expanded later |
| `device_type`             | type such as `camera`, `pm_sensor`, `weather_sensor` | identifies the modality                          |
| `model_name`              | device model                                         | useful for reproducibility                       |
| `manufacturer`            | manufacturer name                                    | useful for documentation                         |
| `communication_interface` | interface such as `CSI`, `UART`, `I2C`               | useful for implementation and debugging          |
| `sampling_interval_sec`   | collection interval in seconds                       | records the intended cadence                     |
| `status`                  | current status such as `active` or `inactive`        | useful operationally                             |
| `notes`                   | additional remarks                                   | flexible field for device-specific comments      |

---

## 7. Raw Data Schemas

## 7.1 `raw/pm_sensor_raw.jsonl`

This file stores raw particulate sensor readings.
One line = one PM sensor event.

### Schema

| Field             | Description                       | Reason                               |
| ----------------- | --------------------------------- | ------------------------------------ |
| `event_id`        | unique identifier for the reading | useful for traceability              |
| `site_id`         | site identifier                   | keeps the record portable            |
| `device_id`       | PM sensor identifier              | links the row to the exact sensor    |
| `timestamp_utc`   | canonical UTC timestamp           | main machine-readable time field     |
| `timestamp_local` | local timestamp                   | useful for manual inspection         |
| `pm25_ug_m3`      | PM2.5 value                       | core air-quality signal              |
| `pm10_ug_m3`      | PM10 value                        | second air-quality signal            |
| `sensor_status`   | success/failure status            | useful for identifying invalid reads |
| `error_code`      | error detail if present           | useful for debugging                 |

### Example

```json
{"event_id":"pm_000001","site_id":"site_godrej_15f","device_id":"pm_01","timestamp_utc":"2026-05-04T00:00:00Z","timestamp_local":"2026-05-04T05:30:00+05:30","pm25_ug_m3":41.2,"pm10_ug_m3":67.8,"sensor_status":"ok","error_code":null}
```

---

## 7.2 `raw/weather_sensor_raw.jsonl`

This file stores raw local weather sensor readings.
One line = one weather sensor event.

### Schema

| Field             | Description                       | Reason                               |
| ----------------- | --------------------------------- | ------------------------------------ |
| `event_id`        | unique identifier for the reading | useful for traceability              |
| `site_id`         | site identifier                   | keeps the record portable            |
| `device_id`       | weather sensor identifier         | links the row to the exact sensor    |
| `timestamp_utc`   | canonical UTC timestamp           | main time field                      |
| `timestamp_local` | local timestamp                   | useful for manual inspection         |
| `temperature_c`   | temperature value                 | local environmental context          |
| `humidity_pct`    | humidity value                    | local environmental context          |
| `pressure_hpa`    | pressure value                    | local environmental context          |
| `sensor_status`   | success/failure status            | useful for identifying invalid reads |
| `error_code`      | error detail if present           | useful for debugging                 |

### Example

```json
{"event_id":"wx_000001","site_id":"site_godrej_15f","device_id":"wx_01","timestamp_utc":"2026-05-04T00:00:00Z","timestamp_local":"2026-05-04T05:30:00+05:30","temperature_c":30.8,"humidity_pct":72.1,"pressure_hpa":1002.6,"sensor_status":"ok","error_code":null}
```

---

## 7.3 `raw/image_manifest.jsonl`

This file stores metadata about each captured image.
The image itself is stored separately as a `.jpg` file under `raw/images/...`.

### Schema

| Field             | Description                     | Reason                                          |
| ----------------- | ------------------------------- | ----------------------------------------------- |
| `image_id`        | unique identifier for the image | useful for linking later                        |
| `site_id`         | site identifier                 | keeps the record portable                       |
| `device_id`       | camera identifier               | links the image to the exact camera             |
| `timestamp_utc`   | canonical UTC timestamp         | main time field                                 |
| `timestamp_local` | local timestamp                 | useful for inspection                           |
| `filename`        | name of the image file          | useful for manual reference                     |
| `relative_path`   | relative path to the image file | keeps the dataset portable across Pi and laptop |
| `width_px`        | image width                     | useful for later preprocessing                  |
| `height_px`       | image height                    | useful for later preprocessing                  |
| `capture_status`  | success/failure status          | useful if capture fails                         |

### Why `relative_path` is used instead of an absolute path

The images are first stored on the Raspberry Pi and later backed up to the laptop.
If an absolute path were stored, it would become invalid after backup.
By storing only the relative path, the same metadata remains valid on both machines.

### Example

```json
{"image_id":"img_000001","site_id":"site_godrej_15f","device_id":"cam_01","timestamp_utc":"2026-05-04T06:00:00Z","timestamp_local":"2026-05-04T11:30:00+05:30","filename":"img_2026-05-04T06-00-00Z.jpg","relative_path":"raw/images/2026-05-04/img_2026-05-04T06-00-00Z.jpg","width_px":1920,"height_px":1080,"capture_status":"ok"}
```

---

## 8. Operational Log Files

The following three log files are kept on the Raspberry Pi:

* `pm_capture.log`
* `weather_capture.log`
* `image_capture.log`

These files are intended only for operational monitoring.

### Purpose

They help identify issues such as:

* sensor read failures,
* camera capture failures,
* skipped image captures outside daytime,
* script restarts,
* file writing problems.

These logs are not part of the scientific dataset itself, but they are useful for troubleshooting and maintaining the pipeline.

---

## 9. Fused Data Schemas

The fused datasets are created **only on the laptop after backup**.
They are stored in two forms:

* `.parquet` for analysis,
* `.csv` for human-readable inspection.

---

## 9.1 `fused/fused_5min/YYYY-MM.parquet` and `YYYY-MM.csv`

These files store 5-minute fused records.

### Fusion logic

For each 5-minute interval:

* PM values are aggregated from the PM sensor readings within that interval,
* weather data are taken from the local weather sensor reading for that interval,
* image data are attached if a daytime image exists in that interval.

### Schema

| Field                  | Description                                  | Reason                                   |
| ---------------------- | -------------------------------------------- | ---------------------------------------- |
| `record_id`            | unique fused record identifier               | useful for traceability                  |
| `site_id`              | site identifier                              | useful for future multi-site analysis    |
| `window_start_utc`     | start of the 5-minute interval               | defines the fused window                 |
| `window_end_utc`       | end of the 5-minute interval                 | defines the fused window                 |
| `anchor_timestamp_utc` | representative timestamp of the fused window | useful for downstream indexing           |
| `image_id`             | linked image ID, if present                  | links image modality to the fused record |
| `relative_path`        | linked image path, if present                | points to the corresponding image        |
| `pm25_mean_ug_m3`      | mean PM2.5 over the interval                 | main fused PM2.5 value                   |
| `pm10_mean_ug_m3`      | mean PM10 over the interval                  | main fused PM10 value                    |
| `temperature_c`        | weather sensor value for that interval       | local environmental context              |
| `humidity_pct`         | weather sensor value for that interval       | local environmental context              |
| `pressure_hpa`         | weather sensor value for that interval       | local environmental context              |
| `pm_sensor_count`      | number of PM readings used in the fusion     | useful for traceability                  |
| `image_available`      | whether an image exists in that interval     | useful because images are daytime-only   |

### Notes

* image-related fields may be `null` outside daytime,
* 5-minute fused rows are still created at night because the sensors run continuously.

---

## 9.2 `fused/fused_hourly/YYYY-MM.parquet` and `YYYY-MM.csv`

These files store hourly fused records.

### Fusion logic

For each hourly interval:

* PM values are aggregated from all PM readings in that hour,
* weather values are aggregated from all weather readings in that hour,
* image count is recorded for the number of images available in that hour.

### Schema

| Field                  | Description                                     | Reason                                                   |
| ---------------------- | ----------------------------------------------- | -------------------------------------------------------- |
| `record_id`            | unique fused record identifier                  | useful for traceability                                  |
| `site_id`              | site identifier                                 | useful for future multi-site analysis                    |
| `window_start_utc`     | start of the hourly interval                    | defines the fused window                                 |
| `window_end_utc`       | end of the hourly interval                      | defines the fused window                                 |
| `anchor_timestamp_utc` | representative timestamp of the fused window    | useful for downstream indexing                           |
| `image_count`          | number of images in the hour                    | useful because image availability changes by time of day |
| `pm25_mean_ug_m3`      | mean PM2.5 over the hour                        | main hourly PM2.5 value                                  |
| `pm10_mean_ug_m3`      | mean PM10 over the hour                         | main hourly PM10 value                                   |
| `temperature_mean_c`   | mean temperature over the hour                  | hourly environmental context                             |
| `humidity_mean_pct`    | mean humidity over the hour                     | hourly environmental context                             |
| `pressure_mean_hpa`    | mean pressure over the hour                     | hourly environmental context                             |
| `pm_sensor_count`      | number of PM rows contributing to the hour      | useful for traceability                                  |
| `weather_sensor_count` | number of weather rows contributing to the hour | useful for traceability                                  |
| `image_available`      | whether at least one image exists in the hour   | useful for downstream filtering                          |

---

## 10. Backup Workflow

The Raspberry Pi acts as the **collection machine**, while the laptop acts as the **backup and processing machine**.

### Backup method

The data are backed up from the Raspberry Pi to the laptop using `rsync` over SSH.

### Example concept

The entire site folder is copied from the Pi to the laptop while preserving the internal folder structure.
Because the image manifest stores only relative paths, the same dataset remains valid after backup.

### Conceptual workflow

1. the Raspberry Pi collects raw data continuously,
2. raw files and images are stored under the site folder,
3. I connect to the Raspberry Pi from my laptop,
4. I back up the site folder using `rsync`,
5. I generate the fused CSV and Parquet files on the laptop from the backed-up raw data.

---

## 11. End-to-End Workflow Summary

The current end-to-end workflow is:

1. define site and device metadata,
2. collect raw PM data continuously on the Raspberry Pi,
3. collect raw weather data continuously on the Raspberry Pi,
4. collect daytime images on the Raspberry Pi,
5. write operational logs on the Raspberry Pi,
6. back up the complete site folder to the laptop,
7. generate 5-minute fused datasets on the laptop,
8. generate hourly fused datasets on the laptop,
9. use CSV for human-readable inspection and Parquet for later analysis and modeling.

---

## 12. Current Intention

At this stage, my aim is to keep the data collection system:

* simple enough to implement reliably,
* explicit in its structure,
* modular across modalities,
* and scalable if additional sites are added later.

I would be very grateful for your approval of this Version 1 workflow, or for any suggestions you may have regarding improvements before I proceed further.

Thank you very much for your guidance.
