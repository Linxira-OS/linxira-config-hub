# Linxira Config Hub

Configuration and diagnostics tools for Linxira OS.

The current supported surface is `cli/linxira-config` for administrator-facing
source, runtime, SSH, network and controlled configuration management. Software installation is owned by
the independent [Linxira Package Center](https://github.com/Linxira-OS/linxira-package-center)
and its `linxira-components` transaction backend. Config Hub does not contain a
Package Center implementation or expose software installation commands. Its
mirror commands cover
Arch, npm, PyPI, AUR, Go modules and explicitly enabled Flatpak remotes.

## Catalog queries

Catalog commands are read-only and accept catalog IDs, never package names or
commands:

```console
linxira-config catalog software --all
linxira-config catalog component --status partial
linxira-config catalog bundle show kde-plasma
```

Catalog v2 compatibility maps `software` to `applications`, `component` to the
legacy `profiles` metadata, and `bundle` to `desktopBundles`. The CLI does not
expand or apply any of these records. By default lists only show `installed`,
`partial`, `external`, `pending`, `drifted`, and `reboot-required`; `--all`
also shows `not-installed` entries. `--status` accepts those states plus
`not-installed` and `unavailable`.

When `/var/lib/linxira/catalog/state-v1.json` is absent, package observation is
reported as `external`, `partial`, or `not-installed`. A state file may provide
managed or pending states using this fixed shape:

```json
{
  "catalogStateVersion": 1,
  "items": [
    {"kind": "software", "id": "firefox", "status": "installed"}
  ]
}
```

`LINXIRA_CATALOG_STATE_PATH` may select another state file for testing.

## SSH keys

`ssh key list/show/fingerprint/generate/remove` manages named Ed25519 key pairs
for the invoking target user. Names are plain basenames, existing keys are never
overwritten, symlinked SSH paths are rejected, generation prompts for a
passphrase, and removal requires `--yes`.

`ssh authorized list/add/remove` manages the same user's `authorized_keys`.
Only one plain public key without `authorized_keys` options is accepted per add;
removal uses an exact SHA256 fingerprint and requires `--yes`. This prevents
forced-command or environment options from becoming a shell execution path.
Existing optioned entries are visible as `optioned` and can be removed, but the
CLI never creates them.

## Runtime contract

- Bash
- `jq`
- `pacman` and standard Arch system tools
- `/usr/share/linxira/catalog/catalog-v3.json` from `linxira-catalog`

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

## License

MIT. See `LICENSE`.
