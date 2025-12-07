import os
import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from PIL import Image
from io import BytesIO

TRAINING_DIR = "training_data"
TARGET_IMAGE_COUNT = 220
IMAGE_SIZE = (256, 256)
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def save_and_crop_images(image_urls, species_folder):
    current_count = len([f for f in os.listdir(species_folder) if f.lower().endswith(".jpg")])
    saved = 0
    for url in image_urls:
        if saved + current_count >= TARGET_IMAGE_COUNT:
            break
        try:
            img_data = requests.get(url, headers=HEADERS, timeout=10).content
            img = Image.open(BytesIO(img_data)).convert("RGB")
            img = img.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
            img.save(os.path.join(species_folder, f"{current_count + saved}.jpg"), quality=75)
            saved += 1
            time.sleep(0.2)
        except Exception as e:
            # print(f"Failed to download or process image: {e}")
            continue
    return saved

def scrape_arachnophoto_images(species_name, needed_count):
    import re
    urls = []
    base_url = "https://www.arachnophoto.com"
    search_name = species_name.lower().replace(" ", "-")
    species_url = f"{base_url}/en/salticidae-2/{search_name}/"

    try:
        r = requests.get(species_url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Method 1: full-resolution links in <a href="...jpg">
        img_links = soup.select("a[href$='.jpg']")
        for link in img_links:
            if len(urls) >= needed_count:
                break
            full_img_url = link.get("href")
            if full_img_url and full_img_url.endswith(".jpg"):
                urls.append(full_img_url)

        # Method 2: backup — extract from <div class="lcl_image_elem" style="background-image: url(...)">
        if len(urls) < needed_count:
            styled_divs = soup.select("div.lcl_image_elem[style]")
            for div in styled_divs:
                if len(urls) >= needed_count:
                    break
                style = div.get("style", "")
                match = re.search(r'url\(&quot;(.*?)&quot;\)', style)
                if match:
                    url = match.group(1)
                    urls.append(url)

        print(f"Arachnophoto: Found {len(urls)} images for {species_name}")

    except Exception as e:
        print(f"Arachnophoto scraping error for {species_name}: {e}")
    return urls




def ensure_images_for_all_species():
    for folder in os.listdir(TRAINING_DIR):
        species_folder = os.path.join(TRAINING_DIR, folder)
        if not os.path.isdir(species_folder):
            continue
        current_count = len([f for f in os.listdir(species_folder) if f.lower().endswith(".jpg")])
        print(f"\n{folder}: {current_count} images")

        if current_count >= TARGET_IMAGE_COUNT:
            print(f"✅ Already have {current_count} images for {folder}, skipping.")
            continue

        needed = TARGET_IMAGE_COUNT - current_count
        species_name = folder.replace("_", " ")

        # Then try BugGuide
        needed = TARGET_IMAGE_COUNT - current_count
        bugguide_urls = scrape_arachnophoto_images(species_name, needed)
        saved = save_and_crop_images(bugguide_urls, species_folder)
        current_count += saved
        print(f"✅ Saved {saved} images from arachnophoto.")

        if current_count < TARGET_IMAGE_COUNT:
            print(f"⚠️ Still only {current_count} images for {species_name}. Consider manual search.")

if __name__ == "__main__":
    ensure_images_for_all_species()
