# Linxira Config Hub

Configuration and diagnostics tools for Linxira OS.

The current supported surface is `cli/linxira-config`. Its workflow commands
read reviewed native profiles and applications from catalog v2 and install only
package names declared by an Arch-source entry. Its mirror commands cover
Arch, npm, PyPI, AUR and explicitly enabled Flatpak remotes.

## Runtime contract

- Bash
- `jq`
- `pacman` and standard Arch system tools
- `/usr/share/linxira/catalog/catalog-v2.json` from `linxira-catalog`

Set `LINXIRA_CATALOG_PATH` to validate the CLI against a catalog outside an
installed Linxira system.

Flatpak remotes remain disabled by default. `mirror flatpak set flathub` is an
explicit opt-in operation and requires the `flatpak` client.
