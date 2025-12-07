import os
import requests
import time
from PIL import Image, ImageOps
from io import BytesIO

# Constants
JUMPING_SPIDER_TAXON_ID = 48139  # Correct Salticidae ID
ONTARIO_PLACE_ID = 6883
QUALITY_GRADE = "research"
TRAINING_DIR = "training_data"
MAX_IMAGES_PER_SPECIES = 220
IMAGE_SIZE = (256, 256)
SLEEP_BETWEEN_REQUESTS = 1


def get_species_list():
    """Get list of Salticidae species in Ontario with at least one research grade observation."""
    url = "https://api.inaturalist.org/v1/observations/species_counts"
    params = {
        "taxon_id": JUMPING_SPIDER_TAXON_ID,
        "place_id": ONTARIO_PLACE_ID,
        "quality_grade": QUALITY_GRADE,
        "verifiable": True
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json().get("results", [])
    return [(entry["taxon"]["id"], entry["taxon"]["name"]) for entry in results]


def fetch_observation_images(taxon_id, max_images, quality='research'):
    """Fetch image URLs for a given taxon_id and quality grade."""
    collected_urls = []
    page = 1
    per_page = 30

    while len(collected_urls) < max_images:
        params = {
            "taxon_id": taxon_id,
            "quality_grade": quality,
            "place_id": ONTARIO_PLACE_ID,
            "photos": True,
            "verifiable": True,
            "per_page": per_page,
            "page": page
        }
        response = requests.get("https://api.inaturalist.org/v1/observations", params=params)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            break
        for obs in results:
            for photo in obs.get("photos", []):
                url = photo["url"].replace("square", "original")
                collected_urls.append(url)
                if len(collected_urls) >= max_images:
                    break
        page += 1
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return collected_urls


def fetch_commons_images(species_name, needed_count):
    """Fetch fallback images from Wikimedia Commons."""
    urls = []
    response = requests.get("https://commons.wikimedia.org/w/api.php", {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": species_name,
        "gsrlimit": needed_count,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 512
    })
    try:
        pages = response.json().get("query", {}).get("pages", {})
        for p in pages.values():
            if "imageinfo" in p:
                urls.append(p["imageinfo"][0]["thumburl"])
    except Exception:
        pass
    return urls


def save_and_crop_images(image_urls, species_name):
    """Download, crop, resize, and save images locally."""
    saved_count = 0
    species_folder = os.path.join(TRAINING_DIR, species_name.replace(" ", "_"))
    os.makedirs(species_folder, exist_ok=True)

    for i, url in enumerate(image_urls):
        try:
            img_data = requests.get(url).content
            img = Image.open(BytesIO(img_data)).convert("RGB")
            img = img.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
            img.save(os.path.join(species_folder, f"{i}.jpg"), quality=75)
            saved_count += 1
        except Exception as e:
            print(e)
        time.sleep(0.2)
    return saved_count


def main():
    os.makedirs(TRAINING_DIR, exist_ok=True)
    species_list = get_species_list()
    print(f"Found {len(species_list)} species.")

    for taxon_id, species_name in species_list:
        print(f"\nProcessing: {species_name}")
        image_urls = []

        # Step 1: Get research grade images
        rg_images = fetch_observation_images(taxon_id, MAX_IMAGES_PER_SPECIES, quality='research')
        image_urls.extend(rg_images)
        print(f"  Got {len(rg_images)} research-grade images.")

        # Step 2: Get non-research-grade if needed
        if len(image_urls) < MAX_IMAGES_PER_SPECIES:
            needed = MAX_IMAGES_PER_SPECIES - len(image_urls)
            non_rg_images = fetch_observation_images(taxon_id, needed, quality='needs_id')
            image_urls.extend(non_rg_images)
            print(f"  Got {len(non_rg_images)} non-research-grade images.")

        # Step 3: Get Wikimedia Commons if still needed
        if len(image_urls) < MAX_IMAGES_PER_SPECIES:
            needed = MAX_IMAGES_PER_SPECIES - len(image_urls)
            commons_images = fetch_commons_images(species_name, needed)
            image_urls.extend(commons_images)
            print(f"  Got {len(commons_images)} Wikimedia images.")

        # Step 4: Warn if still not enough
        if len(image_urls) < MAX_IMAGES_PER_SPECIES:
            print(f"⚠️  Only {len(image_urls)} images found for {species_name}. Consider checking BugGuide manually.")

        # Step 5: Save images
        saved = save_and_crop_images(image_urls[:MAX_IMAGES_PER_SPECIES], species_name)
        print(f"✅  Saved {saved} images for {species_name}.")

main()
