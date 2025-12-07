import os
import time
import torch
import random
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, Subset, random_split
from sklearn.metrics import classification_report

# --- Configuration ---
random.seed(42)
torch.manual_seed(42)

BATCH_SIZE = 32
EPOCHS = 10
IMG_SIZE = 256
DATA_DIR = "training_data"
SAMPLE_LIMIT = 220
LIMITED_CLASSES = {
    "junk_blur_noise",
    "non_salticidae_spiders_flattened",
    "non_spider_decoys_flattened",
    "plant_distractions_flattened"
}
MERGED_CLASS_NAME = "not_a_jumping_spider"

# --- Transforms ---
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])

# --- Load dataset ---
dataset = datasets.ImageFolder(DATA_DIR, transform=transform)

# --- Remap targets ---
original_class_to_idx = dataset.class_to_idx
original_idx_to_class = {v: k for k, v in original_class_to_idx.items()}

# Mapping original class indices → new indices
new_class_names = []
merge_indices = set()

for idx, class_name in original_idx_to_class.items():
    if class_name in LIMITED_CLASSES:
        merge_indices.add(idx)
    else:
        new_class_names.append(class_name)

new_class_names.append(MERGED_CLASS_NAME)
new_class_to_idx = {name: i for i, name in enumerate(new_class_names)}
idx_map = {}

for idx, class_name in original_idx_to_class.items():
    if idx in merge_indices:
        idx_map[idx] = new_class_to_idx[MERGED_CLASS_NAME]
    else:
        idx_map[idx] = new_class_to_idx[class_name]

# --- Group sample indices by new class ---
class_indices = {i: [] for i in range(len(new_class_names))}
for i, (_, original_label) in enumerate(dataset.samples):
    new_label = idx_map[original_label]
    class_indices[new_label].append(i)

# --- Subsample merged class ---
final_indices = []
for label_idx, indices in class_indices.items():
    class_name = new_class_names[label_idx]
    if class_name == MERGED_CLASS_NAME:
        sampled = random.sample(indices, min(SAMPLE_LIMIT, len(indices)))
        final_indices.extend(sampled)
    else:
        final_indices.extend(indices)

# --- Dataset subset ---
subset = Subset(dataset, final_indices)

# Replace targets in subset (override getitem)
class RemappedDataset(torch.utils.data.Dataset):
    def __init__(self, subset, idx_map):
        self.subset = subset
        self.idx_map = idx_map

    def __getitem__(self, index):
        x, original_label = self.subset[index]
        return x, idx_map[original_label]

    def __len__(self):
        return len(self.subset)

# --- Remap labels ---
remapped_dataset = RemappedDataset(subset, idx_map)

# --- Split into training and validation (95% / 5%) ---
val_size = int(0.05 * len(remapped_dataset))
train_size = len(remapped_dataset) - val_size
train_set, val_set = random_split(remapped_dataset, [train_size, val_size])

train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_set, batch_size=BATCH_SIZE, shuffle=False)

# --- Model setup ---
num_classes = len(new_class_names)
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, num_classes)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# --- Loss and optimizer ---
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)

# --- Training loop with validation ---
total_batches = len(train_loader) * EPOCHS
batches_done = 0
batch_times = []

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    start_time = time.time()
    print(f"\nEpoch {epoch+1}/{EPOCHS} starting...")

    for batch_idx, (images, labels) in enumerate(train_loader):
        batch_start = time.time()
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        output = model(images)
        loss = criterion(output, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

        batch_duration = time.time() - batch_start
        batch_times.append(batch_duration)
        batches_done += 1

        avg_batch_time = sum(batch_times) / len(batch_times)
        remaining_batches_epoch = len(train_loader) - (batch_idx + 1)
        remaining_batches_total = total_batches - batches_done

        est_epoch_time = avg_batch_time * remaining_batches_epoch
        est_total_time = avg_batch_time * remaining_batches_total

        print(
            f"Batch {batch_idx+1}/{len(train_loader)} "
            f"- Loss: {loss.item():.4f} "
            f"- Epoch Time Left: {est_epoch_time:.1f}s "
            f"- Total Time Left: {est_total_time:.1f}s"
        )

    epoch_time = time.time() - start_time
    print(f"Epoch {epoch+1} complete. Avg Loss: {total_loss/len(train_loader):.4f} - Time: {epoch_time:.1f}s")

    # --- Validation after each epoch ---
    model.eval()
    val_preds, val_labels = [], []
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            output = model(images)
            preds = output.argmax(dim=1).cpu()
            val_preds.extend(preds)
            val_labels.extend(labels)

    print("\nValidation Report:")
    print(classification_report(
    val_labels,
    val_preds,
    labels=list(range(len(new_class_names))),
    target_names=new_class_names,
    zero_division=0  # Avoid divide-by-zero warnings
))

# --- Save model ---
torch.save(model, "spider_classifier_4_full.pt")
print("\nModel saved to spider_classifier_4_full.pt")
