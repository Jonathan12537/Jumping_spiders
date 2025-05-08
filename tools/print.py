from pathlib import Path
import json

# Get the current script's directory and navigate to the data folder
script_dir = Path(__file__).parent
data_dir = script_dir / ".." / "data"
json_path = data_dir / "jumping_spider_list.json"

# Resolve any '..' in the path
json_path = json_path.resolve()

print(f"Looking for JSON file at: {json_path}")

if json_path.exists():
    with open(json_path, "r") as f:
        data = json.load(f)
        for obj in data:
            print(obj.get("scientific_name", "No scientific name found"))
else:
    print(f"Error: File not found at {json_path}")