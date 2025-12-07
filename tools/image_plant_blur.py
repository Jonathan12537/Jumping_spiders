import os
import requests
import time
from urllib.parse import quote_plus
from PIL import Image, ImageFilter
from io import BytesIO
import numpy as np

# ---- Configuration ----
BASE_DIR = "training_data"
IMAGE_SIZE = (256, 256)
IMAGES_PER_SPECIES = {
    "junk_blur_noise": 1000
}

# ---- Helpers ----
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# ---- Junk Image Generator ----
def generate_noise_images(target_folder, count):
    ensure_dir(target_folder)
    for i in range(count):
        # Random grayscale, blur, or RGB noise variants
        mode = np.random.choice(['grayscale', 'blur', 'rgb'])
        if mode == 'grayscale':
            val = np.random.randint(0, 256)
            img = Image.new('RGB', IMAGE_SIZE, color=(val, val, val))
        elif mode == 'blur':
            array = np.random.randint(0, 256, (IMAGE_SIZE[1], IMAGE_SIZE[0], 3), dtype=np.uint8)
            img = Image.fromarray(array, 'RGB').filter(ImageFilter.GaussianBlur(radius=np.random.uniform(2, 5)))
        else:  # rgb noise
            array = np.random.randint(0, 256, (IMAGE_SIZE[1], IMAGE_SIZE[0], 3), dtype=np.uint8)
            img = Image.fromarray(array, 'RGB')

        img.save(os.path.join(target_folder, f"{i}.jpg"), "JPEG", quality=85)

# ---- Generate Noise Images ----
junk_folder = os.path.join(BASE_DIR, "junk_blur_noise")
if not os.path.exists(junk_folder) or len(os.listdir(junk_folder)) < IMAGES_PER_SPECIES["junk_blur_noise"]:
    print("Generating junk blur/noise images...")
    generate_noise_images(junk_folder, IMAGES_PER_SPECIES["junk_blur_noise"])
else:
    print("Junk noise images already exist, skipping generation.")
