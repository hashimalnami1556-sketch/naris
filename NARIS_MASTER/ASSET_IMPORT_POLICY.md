# Complete Asset Import Policy

## Required inventory fields
- Original filename
- Local source path
- SHA-256
- MIME/type
- Byte size
- Repository destination
- Import status
- Intended Unreal asset class
- Notes / provenance

## Status values
`SOURCE_FOUND` → `IMPORTED` → `INTEGRATED` → `VALIDATED`

## Rule
A repository import is not considered complete until the binary exists in the repository's approved binary storage and its inventory entry is validated.
