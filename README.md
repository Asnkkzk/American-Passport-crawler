# American Passport Crawler

A Playwright script that opens the passport generator page, watches generated task responses, and saves the `preview` and `download` images returned in the response.

## Requirements

- Python 3.9 or newer
- Windows and PowerShell

## Install

From the repository root:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Run

```powershell
python .\p.py
```

The script opens Chromium. Click Generate in that browser window. When the task response contains `data.preview` or `data.download`, the script attempts to save the corresponding image automatically. Close the browser window when finished.

Downloaded images are stored in `downloaded_images/` and are excluded from Git.
