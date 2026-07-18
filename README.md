# Linxira Config Hub

Configuration and diagnostics tools for Linxira OS.

The current supported surface is `cli/linxira-config`. Its workflow commands
read reviewed native profiles from catalog v2 and install only package names
declared by an Arch-source profile.

## Runtime contract

- Bash
- `jq`
- `pacman` and standard Arch system tools
- `/usr/share/linxira/catalog/catalog-v2.json` from `linxira-catalog`

Set `LINXIRA_CATALOG_PATH` to validate the CLI against a catalog outside an
installed Linxira system.
