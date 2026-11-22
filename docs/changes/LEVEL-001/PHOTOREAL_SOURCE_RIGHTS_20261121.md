# LEVEL-001 — Photoreal Jeddah external asset/data rights screen

Date: 2026-11-21. **Research only. No external 3D mesh or imagery downloaded/imported.** Do not treat availability of a photogrammetric reference as permission to use it in a game.

## Approved factual geospatial foundation
- Existing user-held OSM cache supplies true street geometries and building footprint outlines used for isolated review03 (189 building polygons / 64 eligible road ways in 500m Al-Balad sector). © OpenStreetMap contributors, ODbL 1.0: https://www.openstreetmap.org/copyright
- Source dates, attributed contributor credits, user/distribution obligations and database derivative policies must be reviewed for shipping.
- Heights in the current V3 are defaults or OSM fields, not surveyed building elevations. Original V2 buildings were axis-aligned rectangular proxies. V3 keeps true 2D outlines but lacks faithful wall elevations and photographed materials.

## Real source candidates and licensing decisions
1. **Open Heritage 3D — Al Balad Sami Office**, https://openheritage3d.org/project.php?id=zd5x-jm42 (2022 publish; 2012 capture). Lists 0.6 GB terrestrial photogrammetry and ~1 GB 3D derivatives; license **CC BY-NC-ND**, reuse score **C — Non-Metric Model**. **Reference only — REJECT direct game integration or derivative production pending express separate authorization**. Their description warns reconstructions are not well constrained.
2. **Open Heritage 3D — Al Balad Tree Plaza**, https://openheritage3d.org/project.php?id=8rsc-c102 (2022 publication; 2012 capture). Same **CC BY-NC-ND**, reuse score **C**. **Reference only**, 1 GB 3D data not licensed for normal commercial derivative workflows without separate permission.
3. **UCL Jeddah historic building BIM work**, https://www.ucl.ac.uk/engineering/research-projects/2017/sep/jeddah-historic-building-information-model. Describes terrestrial scanning and photogrammetry for heritage documentation. This does **not** establish asset licensing or downloadable interoperable meshes. Research reference, not an import source.
4. **UNESCO Historic Jeddah**, https://whc.unesco.org/en/list/1361/ — source for verified urban heritage context. Photographs and documentary materials have their own rights; do not harvest for PBR textures without permission.
5. **Google Photorealistic 3D Tiles / Cesium for Unreal**, https://cesium.com/learn/unreal/unreal-photorealistic-3d-tiles/ . Google country coverage (https://developers.google.com/maps/coverage) lists Saudi Arabia Map Tiles 2D/3D as supported at the country level but Maps JavaScript 3D as unavailable. This **does not prove that photorealistic building tiles cover the requested 500m Al-Balad area**, nor does it grant game redistribution or offline extraction rights. Require a licensed API account, geographic coverage test and provider-specific legal review before trial in an Unreal level.

## Recommended implementation gate
- Keep the existing OSM-derived 3D urban footprint mesh as an accurate **blockout**. Do not remodel street positions from concept art.
- Build a **new, original** modular Hijazi facade kit (rawasheen/window projections, plaster/masonry, doors, shopfronts, roof ornaments) from either measurements, original user-supplied/authorized photos, or independently authored PBR materials; record provenance per asset.
- Validate placement against mapped building footprints and locally reviewed reference imagery for geometry and scale. Avoid claiming all 189 building facades are historically identical; only tag confirmed buildings as heritage.
- Install/display on isolated REVIEW map, not the shipping map, test point lights/exposure and correct nightly visibility, then run deterministic same-camera **Lit-before vs Lit-after** QA and 2-client network/gameplay/BuildCookRun. Stop if resource preflight fails.
- Keep vendor license & attribution text in `docs/changes/LEVEL-001` and later shipped game credits only after confirming permissions.

## Current blocker
A diagnostic UE lit-vs-unlit comparison has been saved on workstation; unlit displays true OSM geometry while Lit is severely underilluminated. Corrective lighting requires shader compilation. A previous run failed because C: filled; a local read-only preflight script (`Saved/GIS/Jeddah/LEVEL001_resource_preflight.ps1`) blocks heavy work under 30 GiB free disk, 8 GiB available RAM or another Unreal editor job. Latest observed disk measurements fluctuated significantly as separate jobs ran. No project files or caches were broadly deleted. Do not declare this level photoreal or ready for shipping.
