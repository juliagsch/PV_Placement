from utils import get_building_filenames
import os

filenames = get_building_filenames()

for file in filenames:
    parts = file.split('_')
    x_min = float(parts[0])
    y_min = float(parts[1])
    x_max = float(parts[2])
    y_max = float(parts[3])

    if x_max-x_min > 50 or y_max-y_min > 50:
        print("Removing ", file)
        os.remove(f"./buildings/{file}")
        os.remove(f"./roofs/{file}")

