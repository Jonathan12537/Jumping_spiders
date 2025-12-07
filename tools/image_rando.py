import os
import requests
import time
from urllib.parse import quote_plus
from PIL import Image
from io import BytesIO

# ---- Configuration ----
BASE_DIR = "training_data"
IMAGE_SIZE = (256, 256)
IMAGES_PER_SPECIES = {
    "jumping_spiders_non_ontario": 200,
    "non_salticidae_spiders": 200,
    "non_spider_decoys": 150
}

# ---- Species Groups ----
species_groups = {
    "jumping_spiders_non_ontario": [
        "Baryphas ahenus", "Hyllus argyrotoxus", "Thyene natalii", "Portia schultzi",
        "Cosmophasis micarioides", "Helpis minitabunda", "Apricia jovialis",
        "Zenodorus orbiculatus", "Clynotis severus", "Maratus pavonis",
        "Cosmophasis thalassina", "Sandalodes superbus"
    ],
    "non_salticidae_spiders": [
        "Araneus diadematus", "Misumena vatia", "Pisaura mirabilis", "Dolomedes tenebrosus",
        "Steatoda grossa", "Larinioides cornutus", "Dolomedes triton",
        "Tegenaria domestica", "Dolomedes scriptus", "Misumenoides formosipes",
        "Philodromus dispar"
    ],
    "non_spider_decoys": [
        "Nomada goodeniana", "Musca domestica", "Dolichovespula maculata",
        "Vespula germanica", "Anoplotrupes stercorosus", "Photinus pyralis",
        "Tapinoma sessile", "Camponotus pennsylvanicus", "Solenopsis invicta",
        "Scutigera coleoptrata"
    ]
}

# ---- Functions ----
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_inaturalist_photos(species_name, max_images):
    photos = []
    page = 1
    while len(photos) < max_images:
        url = f"https://api.inaturalist.org/v1/observations?taxon_name={quote_plus(species_name)}&photos=true&page={page}&per_page=30"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Failed to fetch observations for {species_name}")
            break
        results = resp.json().get("results", [])
        if not results:
            break
        for obs in results:
            for photo in obs.get("photos", []):
                url = photo.get("url")
                if url:
                    # Replace square size (like square) with original format
                    url = url.replace("square", "original")
                    photos.append(url)
                    if len(photos) >= max_images:
                        break
            if len(photos) >= max_images:
                break
        page += 1
        time.sleep(1)  # Be polite to the API
    return photos

def download_and_save_images(image_urls, target_folder):
    ensure_dir(target_folder)
    existing_files = os.listdir(target_folder)
    next_index = len(existing_files)
    for url in image_urls:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img = img.resize(IMAGE_SIZE)
            save_path = os.path.join(target_folder, f"{next_index}.jpg")
            img.save(save_path, "JPEG", quality=85)
            next_index += 1
        except Exception as e:
            print(f"Failed to process image: {e}")

# ---- Main Execution ----
for group, species_list in species_groups.items():
    target_per_species = IMAGES_PER_SPECIES[group]
    for species in species_list:
        folder_name = os.path.join(BASE_DIR, group, species.replace(" ", "_"))
        if os.path.exists(folder_name) and len(os.listdir(folder_name)) >= target_per_species:
            print(f"Skipping {species} (already has enough images)")
            continue
        print(f"Fetching images for: {species}")
        urls = get_inaturalist_photos(species, target_per_species)
        print(f"found {len(urls)} images Downloading")
        download_and_save_images(urls, folder_name)
