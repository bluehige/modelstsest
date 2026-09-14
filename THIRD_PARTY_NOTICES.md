# Third-party provenance

Reference: https://github.com/octopus7/astra-blender-forest
License: MIT, Copyright (c) 2026 octopus7.
Inspected: 2026-09-14, `main`.

Reviewed source files:
- `Cozy_Lake_Forest_300m/cozy_mesh_library.py`, blob `950de506298543ec1e822605dd7c98064c92f82c`.
- `Cozy_Lake_Forest_300m/01_build_scene.py`, blob `ccbfcc15b203a3889424430f2635162665a9b39c`.
- Root README_KO and LICENSE.

`cozy_city/mesh.py` adapts polygon triangulation, box winding, capped tubes,
icosahedron topology, and deterministic mesh recipe concepts from the upstream.
`assets.py` adapts its branch-and-faceted-canopy visual approach; city buildings,
roads, props, and block layout are new. The Blender integration preserves its
shared-mesh, separate-owned-scene and vertex-colour principles.

No upstream binary models, generated images, texture atlases or Unreal scripts
are redistributed. This is an adaptation, not an official upstream release.
No paid services, external fonts or model downloads are required by the generator.
