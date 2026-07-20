# Linxira Config Hub

Configuration and diagnostics tools for Linxira OS.

The current supported surface is `cli/linxira-config` for administrator-facing
source, runtime and configuration management. Software installation is owned by
the independent [Linxira Package Center](https://github.com/Linxira-OS/linxira-package-center)
and its `linxira-components` transaction backend. Config Hub does not contain a
Package Center implementation or expose software installation commands. Its
mirror commands cover
Arch, npm, PyPI, AUR, Go modules and explicitly enabled Flatpak remotes.

## Runtime contract

- Bash
- `jq`
- `pacman` and standard Arch system tools
- `/usr/share/linxira/catalog/catalog-v2.json` from `linxira-catalog`

Set `LINXIRA_CATALOG_PATH` to validate the CLI against a catalog outside an
installed Linxira system.

Flatpak remotes remain disabled by default. `mirror flatpak set flathub` is an
explicit opt-in operation and requires the `flatpak` client.

Go proxy changes are persisted through `go env -w`; the configured proxy is
used with `direct` fallback. `mirror go reset` restores `proxy.golang.org`.

Conda configuration is intentionally limited to Miniforge. The CLI refuses to
modify a generic Conda installation and only allows the reviewed channel IDs
`conda-forge` and `bioconda`; both can be enabled together with strict channel
priority. Anaconda `defaults` is not configured or enabled by Linxira.
