import os
import requests
from urllib.parse import urlparse
import uuid
import hashlib

def get_file_hash(filepath):
    """Generate a hash for a file to detect duplicates."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def fetch_images(urls):
    save_dir = "Fetched_Images"
    os.makedirs(save_dir, exist_ok=True)

    downloaded_hashes = set()

    for url in urls:
        url = url.strip()
        if not url:
            continue

        print(f"\n🔗 Processing: {url}")

        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()

            # --- Precautions: Check HTTP headers ---
            content_type = response.headers.get("Content-Type", "")
            content_length = response.headers.get("Content-Length")

            if not content_type.startswith("image/"):
                print("⚠️ Skipped: Not an image file.")
                continue

            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10 MB limit
                print("⚠️ Skipped: File too large.")
                continue

            # Extract filename or generate one
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = f"image_{uuid.uuid4().hex}.jpg"

            filepath = os.path.join(save_dir, filename)

            # Save image temporarily
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            # --- Duplicate prevention using hash ---
            file_hash = get_file_hash(filepath)
            if file_hash in downloaded_hashes:
                print("⚠️ Duplicate detected, removing file.")
                os.remove(filepath)
                continue
            else:
                downloaded_hashes.add(file_hash)

            print(f"✅ Image saved: {filepath}")

        except requests.exceptions.MissingSchema:
            print("⚠️ Invalid URL (missing http/https).")
        except requests.exceptions.ConnectionError:
            print("⚠️ Connection error.")
        except requests.exceptions.Timeout:
            print("⚠️ Request timed out.")
        except requests.exceptions.HTTPError as e:
            print(f"⚠️ HTTP error: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")

if __name__ == "__main__":
    print("🌍 Ubuntu Image Fetcher")
    print("Enter multiple URLs (comma-separated):")
    user_input = input(">> ")
    urls = user_input.split(",")
    fetch_images(urls)
