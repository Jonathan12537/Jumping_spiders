import json
import requests
import time

place_id = 6883  # Ontario
jumping_spider_taxon_id = 367200  # Salticidae (Jumping Spiders)
per_page = 200  # Max per iNaturalist API

def fetch_spiders_in_ontario():
    all_species = {}
    page = 1
    while True:
        url = (
            f"https://api.inaturalist.org/v1/observations/species_counts"
            f"?place_id={place_id}&taxon_id={jumping_spider_taxon_id}"
            f"&quality_grade=research&verifiable=true&rank=species&per_page={per_page}&page={page}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch species list: {response.status_code}")
            break
        data = response.json()
        results = data.get("results", [])
        if not results:
            break
        for entry in results:
            taxon = entry.get("taxon", {})
            name = taxon.get("name")
            count = entry.get("count", 0)
            if name:
                all_species[name] = count
        page += 1
        time.sleep(1)  # Be polite to the API
    return all_species

# Step 1: Fetch updated sightings from iNaturalist
print("Fetching all jumping spider species observed in Ontario...")
sightings_data = fetch_spiders_in_ontario()

# Step 2: Load existing data (if any)
try:
    with open("../data/jumping_spider_list.json", "r") as f:
        existing_spiders = {s["scientific_name"]: s for s in json.load(f)}
except FileNotFoundError:
    existing_spiders = {}

# Step 3: Merge and update spider list
updated_spiders = []
for sci_name, count in sightings_data.items():
    if count > 0:
        spider = existing_spiders.get(sci_name, {"scientific_name": sci_name})
        spider["sightings"] = count
        updated_spiders.append(spider)

# Step 4: Save the updated list
with open("../data/jumping_spider_list.json", "w") as f:
    json.dump(updated_spiders, f, indent=2)

print(f"Updated spider list saved with {len(updated_spiders)} species.")
