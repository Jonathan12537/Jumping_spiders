import time
import requests

# Constants
JUMPING_SPIDER_TAXON_ID = 48139  # Salticidae
ONTARIO_PLACE_ID = 6883
QUALITY_GRADE = 'research'

def get_species_in_ontario_with_counts():
    url = "https://api.inaturalist.org/v1/observations/species_counts"
    params = {
        "taxon_id": JUMPING_SPIDER_TAXON_ID,
        "place_id": ONTARIO_PLACE_ID,
        "quality_grade": QUALITY_GRADE,
        "verifiable": True
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    species_data = response.json()["results"]

    species_list = []
    for entry in species_data:
        taxon_id = entry["taxon"]["id"]
        name = entry["taxon"]["name"]
        count = get_photo_count_for_species(taxon_id)
        if count >= 200:
            count = 200
        species_list.append((name, count))
        print(f"{name}: {count} images")
        time.sleep(1)
    return species_list

def get_photo_count_for_species(taxon_id):
    url = "https://api.inaturalist.org/v1/observations"
    params = {
        "taxon_id": taxon_id,
        # "place_id": ONTARIO_PLACE_ID,
        "quality_grade": QUALITY_GRADE,
        "photos": True,
        "verifiable": True,
        "per_page": 1,
        "page": 1
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()["total_results"]
    return results

# Run the script
species_with_counts = get_species_in_ontario_with_counts()

total = 0
for species, img_count in species_with_counts:
    total += img_count

print(f"{total} total images")