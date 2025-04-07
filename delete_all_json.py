import os
import glob

# Match all JSON files in current directory
json_files = glob.glob("*.json")

for file in json_files:
    try:
        os.remove(file)
        print(f"🗑️ Deleted: {file}")
    except Exception as e:
        print(f"❌ Failed to delete {file}: {e}")
