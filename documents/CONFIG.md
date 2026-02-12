# EDLA Configuration

**Author:** R.W. Harper  
**Last Updated:** 2026-02-12  
**License:** GPL-3.0

EDLA does not embed local paths or API keys in code. Use an external config file for machine-specific or sensitive settings.

## Setup (two options)

### Option A: Interactive setup (recommended when no config exists)

If **`edla_config.json`** does not exist, EDLA will show a **Configuration Setup** dialog on startup. You can:

- Enter the Elite Dangerous log directory and app data directory (or leave blank to use defaults).
- Use **Browse** to pick folders.
- Click **Use defaults for all paths** to leave paths empty and use built-in defaults.
- Optionally enter an API key.
- Click **Save and continue** to create `edla_config.json` and start the app.

If you click **Cancel**, the application exits without creating a config file. Next run will show the setup again until you save or create the file manually.

### Option B: Manual setup

1. **Copy the sample config** into the same folder as the application (next to `main.py` or the executable):
   ```text
   copy edla_config.sample.json edla_config.json
   ```

2. **Edit `edla_config.json`** with your paths and optional keys. Leave a value empty (`""`) to use the default.

3. **Do not commit `edla_config.json`** to version control. It is listed in `.gitignore`.

## Config file location

- The application looks for **`edla_config.json`** in the **application base directory** (folder containing `main.py` or the executable).
- If the file is missing, EDLA shows the interactive setup dialog (Option A). If you cancel, the app exits; it does not use built-in defaults until a config file exists (with optional empty values for defaults).

## Options

| Key             | Description                                                                 | Default |
|-----------------|-----------------------------------------------------------------------------|---------|
| `log_dir`       | Elite Dangerous journal folder (e.g. `...\Saved Games\...\Elite Dangerous`) | `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous` |
| `app_data_dir`  | EDLA data folder (profiles, session database)                              | `%USERPROFILE%\.edla` |
| `api_key`       | Optional API key for future integrations; leave empty if unused            | (none)  |

Paths may use environment variables (e.g. `%USERPROFILE%` on Windows or `$HOME` on Unix-style shells where supported).

## Example (Windows)

```json
{
  "log_dir": "C:\\Users\\YourName\\Saved Games\\Frontier Developments\\Elite Dangerous",
  "app_data_dir": "C:\\Users\\YourName\\.edla",
  "api_key": ""
}
```

To use defaults for paths, omit the keys or set them to `""`.

---

## Keeping the repo clean for distribution

The following are excluded from the repo (via `.gitignore`) so the repository stays free of local data and is safe to distribute:

| Excluded | Description |
|----------|-------------|
| `edla_config.json` | Your paths and API keys (use the sample as template). |
| `.edla/` | User app data (profiles, session database). |
| `logs/` | All application log files. |
| `app_error.log` | Fallback error log (when `logs/` is unavailable). |
| `*.log` | Any other log files in the tree. |
| `build/`, `dist/` | PyInstaller build output. |

Do not commit these. Clone or download the repo gives a clean copy with no user data or logs.
