import torch
from torchvision import transforms
from PIL import Image
import os

# Configuration
IMG_SIZE = 256
MODEL_PATH = "spider_classifier_3_full.pt"
TEST_DIR = "testing_data"
TRAIN_DIR = "training_data"

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Class names (ensure correct order!)
CLASS_NAMES = sorted(os.listdir(TRAIN_DIR))

# Load entire model (since torch.save(model) was used)
model = torch.load(MODEL_PATH, map_location=device, weights_only=False)
model.to(device)
model.eval()

# Transform (must match training)
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])

def predict_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        image_tensor = transform(image).unsqueeze(0).to(device)
        with torch.no_grad():
            output = model(image_tensor)
            print("Raw output:", output)
            pred_idx = output.argmax(dim=1).item()
            confidence = torch.softmax(output, dim=1)[0, pred_idx].item()
            return CLASS_NAMES[pred_idx], confidence
    except Exception as e:
        return f"Error: {e}", 0.0


# Loop through testing_data
for root, _, files in os.walk(TEST_DIR):
    for file in files:
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            full_path = os.path.join(root, file)
            label, conf = predict_image(full_path)
            print(f"{full_path} → {label} ({conf:.2%})")
