# NARIS Binary Assets

This directory is the canonical destination for binary project assets: concept art, reference images, PDFs, videos, renders, and future Unreal source/export packages.

## Manifest

`BINARY_ASSETS_MANIFEST.csv` contains the local source inventory, byte size, MIME type, and SHA-256 checksum for every binary/text project file present in the current project workspace.

## Integrity rule

When a binary is uploaded, verify its SHA-256 against the manifest before treating the repository copy as authoritative.

## Current repository limitation

The connected GitHub workflow available in this session can create/update UTF-8 files and Git blobs, but it does not expose a local-file upload parameter or Git LFS/release-asset upload operation. Therefore the binary inventory is recorded now, while the actual binary payloads require a binary-capable Git transport (Git LFS or a release-asset upload) rather than silently substituting links or empty placeholder files.

Do not create fake binary files or rename text into binary extensions.
