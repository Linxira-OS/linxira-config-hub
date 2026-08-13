# Linxira Config Hub

Configuration and diagnostics tools for Linxira OS.

The current supported surface is `cli/linxira-config` for administrator-facing
source, runtime, SSH, network and controlled configuration management. General
software management is owned by Shelly, while curated application setup is owned
by Quick System Software Setup and its `linxira-components` transaction backend.
Config Hub does not contain a software-center implementation or expose software
installation commands. Its mirror commands cover
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

## SSH quick start (turn this machine into a server)

Enable and start the SSH daemon (current test builds gate `ssh on/off` behind
the pending transactional backend, so use the equivalent command):

```console
sudo systemctl enable --now sshd
sudo ufw allow ssh          # only if UFW is active
linxira-config ssh status   # verify: Service state: active
```

Generate a key pair on the client you connect *from*:

```console
linxira-config ssh key generate            # Ed25519, ~/.ssh/id_ed25519
linxira-config ssh key show                # copy the public key line
```

Authorize it on the server (plain public keys only, by design):

```console
echo 'ssh-ed25519 AAAA... user@host' > /tmp/key.pub
linxira-config ssh authorized add /tmp/key.pub && rm /tmp/key.pub
linxira-config ssh authorized list
```

Connect from the client (IP shown in `ssh status` → `Connect:`):

```console
ssh user@server-ip
```

Security notes: disable `PasswordAuthentication` in
`/etc/ssh/sshd_config` before exposing to the public internet, and keep the
firewall on. See the full tutorial at
<https://linxira-os.github.io/docs/remote-access/> (or `/zh/docs/remote-access/`).

## Headless mode (desktop ⇄ server, runtime switch)

`headless on/off/status` switches the running system between the KDE desktop
and a headless server state, freeing the memory the desktop would otherwise
consume for computation tasks:

```console
linxira-config headless on       # desktop disabled from next boot
linxira-config headless on now   # switch immediately (interactive confirm)
linxira-config headless off      # restore desktop from next boot
linxira-config headless off now  # switch back immediately
linxira-config headless status   # current target (multi-user vs graphical)
```

`on now` stops the display manager and terminates the current desktop session
(unsaved data is lost — the CLI asks for confirmation on a TTY). The switch is
`systemctl isolate multi-user.target`; the reverse restarts SDDM. Use SSH or a
TTY to switch back.

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
