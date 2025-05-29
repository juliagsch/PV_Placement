import os

def get_roof_filenames():
    return [f for f in os.listdir(f"./roofs/") if f.endswith('.obj')]

def get_roof_filepaths():
    return [f"./roofs/{f}" for f in os.listdir(f"./roofs/") if f.endswith('.obj')]

def get_building_filenames():
    return [f for f in os.listdir(f"./buildings/") if f.endswith('.obj')]

def get_building_filepaths():
    return [f"./buildings/{f}" for f in os.listdir(f"./buildings/") if f.endswith('.obj')]
