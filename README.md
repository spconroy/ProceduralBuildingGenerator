### ProceduralBuildingGenerator
Blender addon for procedurally generating buildings.

### Compatibility
This addon is compatible with Blender 4.0+ (tested on Blender 5.0).

Originally written for Blender 2.79 by Luka Simic. Ported to modern Blender API (collections, annotation-style properties, sidebar panels, updated matrix operators). Also supports headless/background generation for batch export workflows.

### Installation
Clone or download the repository.
Copy the ProceduralBuildingGenerator folder to your Blender addons directory.
This addon requires no additional Python libraries.

### Usage
The addon panel is in the 3D Viewport Sidebar (N panel) under the "PBG" tab.
After changing parameters, click Generate to create a building.

WARNING: using unreasonably large values might cause Blender to crash due to lack of memory.
WARNING: using incompatible param values might cause Blender to crash due to no validation existing.
NOTE: delete the previous building before generating the new one to see the changes better.

### License
GPL-3.0
