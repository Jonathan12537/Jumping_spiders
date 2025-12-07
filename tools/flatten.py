import os
import shutil

BASE_DIR = "training_data"
FOLDERS_TO_FLATTEN = [
    "jumping_spiders_non_ontario",
    "non_salticidae_spiders",
    "non_spider_decoys",
    "plant_distractors"
]

for category in FOLDERS_TO_FLATTEN:
    source_dir = os.path.join(BASE_DIR, category)
    target_dir = os.path.join(BASE_DIR, f"{category}_flattened")
    os.makedirs(target_dir, exist_ok=True)

    for species_folder in os.listdir(source_dir):
        species_path = os.path.join(source_dir, species_folder)
        if not os.path.isdir(species_path):
            continue

        for filename in os.listdir(species_path):
            src_file = os.path.join(species_path, filename)
            if os.path.isfile(src_file):
                new_name = f"{species_folder}_{filename}"
                dst_file = os.path.join(target_dir, new_name)

                # Avoid overwriting by adding a suffix if needed
                count = 1
                base, ext = os.path.splitext(new_name)
                while os.path.exists(dst_file):
                    new_name = f"{base}_{count}{ext}"
                    dst_file = os.path.join(target_dir, new_name)
                    count += 1

                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} to {dst_file}")

print("Flattening complete!")
