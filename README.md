## Creating building and roof meshes

1. Download .gml files from https://www.swisstopo.admin.ch/en/landscape-model-swissbuildings3d-3-0-beta. I would advice against including patches of large cities as they are very large and many buildings will not be residential. A tile on the countryside may include around 1000-3000 buildings (depends a lot on the area). The files should be saved to ./tiles/buildings
2. Download .xyz files from https://www.swisstopo.admin.ch/en/height-model-swisssurface3d-raster. Important: Those have to cover all of the area already downloaded in step (1). The files should be saved to ./tiles/area
3. Run create_dataset.py to generate a dataset from the downloaded data. This may take a (long) while depending on how many tiles were downloaded
4. Run visualize.py to verify if the samples were processed correctly.

Things to consider:

- Make sure to define reasonable size constraints in create_dataset.py such that suitable buildings will be included in the dataset (not too small or too large). The buildings dataset from Swisstopo contains ANY buildings, this includes sheds or large commercial buildings which might not be suitable for your use case.
- You could unite buildings which are less than x meters away from each other as they likely belong to the same property.
- You may reduce the data size by for example excluding surrounding faces if they are lower than the lowest point of the roof or by computing a convex/concave hull.
