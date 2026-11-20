"""Download preview and download images from generated task responses."""
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PAGE_URL = "https://kyc-helper.org/en/"
OUT_DIR = Path(__file__).resolve().parent / "downloaded_images"


def main():
    OUT_DIR.mkdir(exist_ok=True)
    seen = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        def on_response(response):
            if "/passport-generator/query_task/" not in response.url:
                return
            try:
                payload = response.json()
                data = payload.get("data", {}) if isinstance(payload, dict) else {}
                if not isinstance(data, dict):
                    print(f"Unexpected task response: {payload}", flush=True)
                    return
                print(f"Task status: {data.get('status', 'unknown')}", flush=True)
                for field in ("preview", "download"):
                    filename = data.get(field)
                    if not filename:
                        print(f"No data.{field} in this response yet", flush=True)
                        continue
                    key = (field, str(filename))
                    if key in seen:
                        continue
                    seen.add(key)
                    # The API returns filenames; the site's image files are under this directory.
                    image_url = "https://kyc-helper.org/static/downloads/" + str(filename).lstrip("/")
                    image_response = context.request.get(image_url, timeout=60000)
                    if not image_response.ok:
                        print(f"{field} download failed: HTTP {image_response.status} {image_url}", flush=True)
                        continue
                    suffix = Path(urlparse(str(filename)).path).suffix or ".jpg"
                    target = OUT_DIR / f"{field}_{len(seen)}{suffix}"
                    target.write_bytes(image_response.body())
                    print(f"Saved {field}: {target}", flush=True)
            except Exception as exc:
                print(f"Could not process task response: {exc}", flush=True)

        page.on("response", on_response)
        page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=60000)
        print("Browser open. Generate the image in this window. Preview and download files save automatically.", flush=True)
        print("Close the browser window when finished.", flush=True)
        try:
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass
        browser.close()


if __name__ == "__main__":
    main()
